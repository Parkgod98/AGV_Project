# 보미 — 트러블슈팅

개발 과정에서 마주친 주요 문제와 해결 방법을 기록합니다.

---

## 목차

1. [Jetson 자원 부족 — 라인 트레이싱 중 객체 검출 실패](#1-jetson-자원-부족--라인-트레이싱-중-객체-검출-실패)
2. [LLM API 과호출로 인한 사용량 급증](#2-llm-api-과호출로-인한-사용량-급증)
3. [Pick & Place 후 라인 트레이싱 실패 (빙글빙글)](#3-pick--place-후-라인-트레이싱-실패-빙글빙글)
4. [WiFi 환경에서 MQTT 메시지 유실](#4-wifi-환경에서-mqtt-메시지-유실)
5. [카메라 자원 점유 충돌 — CSI·USB 웹캠 분리](#5-카메라-자원-점유-충돌--csiusb-웹캠-분리)
6. [카메라 실시간 스트림 + YOLO 동시 처리 시 UI 렉](#6-카메라-실시간-스트림--yolo-동시-처리-시-ui-렉)

---

## 1. Jetson 자원 부족 — 라인 트레이싱 중 객체 검출 실패

**증상**

라인 트레이싱(ResNet-18)과 객체 검출(YOLOv5s TFLite)을 동시에 상시 구동하면 Jetson Nano의 GPU/메모리 자원 부족으로 추론 지연이 발생하여 객체를 제때 감지하지 못했다.

**원인**

ResNet-18은 CUDA fp16으로 상시 추론 중이다:

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
use_fp16 = (device.type == "cuda")
# [OK] model loaded | device=cuda fp16=True
```

Jetson Nano(Maxwell GPU, 128 CUDA cores, 4GB LPDDR4 shared)는 두 딥러닝 모델을 동시 상시 구동하기에 자원이 충분하지 않다. ResNet-18은 주행 중 항상 필요하지만 YOLOv5s TFLite는 목적지 도착 후 Pick & Place 시에만 필요하다.

**해결**

**온디맨드 모델·카메라 스위칭** 전략으로 자원 충돌을 원천 차단. 메인 루프(`_line_loop`)가 state에 따라 두 모드를 교대로 실행한다:

```python
# jetson.ipynb — _line_loop()  [Step 4 Final: Resource Optimized]

# ── 주행 모드 ──────────────────────────────────────────────
# ResNet-18(CUDA fp16) 상시 추론, USB 웹캠은 닫힌 상태
with state_lock: state = "running"
# ... ResNet-18 조향 추론 → 모터 제어 반복 ...

# ── 목적지 도착 감지 ───────────────────────────────────────
# arrive_t0 기준으로 일정 시간 이상 목표 waypoint 인접 시 도착 판정

# ── 작업 모드 전환 ─────────────────────────────────────────
with state_lock: state = "working"
execute_work_logic(current_task_type, curr_dest_name)
# execute_work_logic 내부에서 USB 웹캠 오픈 → YOLOv5s TFLite 추론 → 웹캠 클로즈

flush_camera(10)  # CSI 버퍼 클리어 후 주행 모드로 복귀
with state_lock: state = "running"
```

두 모드가 절대 동시에 실행되지 않으므로 ResNet-18(CUDA)과 YOLOv5s TFLite가 자원을 충돌 없이 순차 점유.

---

## 2. LLM API 과호출로 인한 사용량 급증

**증상**

운영 브리핑 기능(`GET /api/interactions/insight`)이 대시보드 갱신 주기마다 GPT-5 API를 반복 호출하여 API 사용량이 불필요하게 많아졌다.

**원인**

Node-RED 플로우가 데이터 변화 여부와 무관하게 매 HTTP 요청마다 OpenAI API를 호출하는 구조였다. 대시보드가 짧은 폴링 주기로 엔드포인트를 반복 호출하면서 문제가 증폭되었다.

**해결**

Node-RED 글로벌 변수를 활용한 **결과 캐싱** 로직 적용:

```javascript
// Node-RED — INSIGHT: build + aggregate
const ttlMs = 3 * 60 * 1000; // 3분 캐시
const now = Date.now();

const cacheKey = "interactionInsightCache";
const cache = global.get(cacheKey) || {};
const cached = cache[range]; // range: "day" | "week"

if (!refresh && cached && (now - cached.generated_at) < ttlMs) {
  return [null, httpOut({ ...cached, cached: true })]; // 캐시 히트 → 즉시 반환
}
// 캐시 미스 or TTL 만료 → OpenAI 호출로 진행
```

```javascript
// Node-RED — INSIGHT: parse + respond (OpenAI 응답 후)
const cache = global.get(cacheKey) || {};
cache[range] = { ...out, generated_at: Date.now() };
global.set(cacheKey, cache); // 결과 저장
```

- TTL **3분**, range(`day`/`week`)별로 독립 캐싱
- `?refresh=1` 쿼리로 강제 갱신 가능

불필요한 중복 호출 제거로 API 비용 절감 및 응답 속도 개선.

---

## 3. Pick & Place 후 라인 트레이싱 실패 (빙글빙글)

**증상**

물체를 집어 올린 후 주행을 재개하면 라인을 찾지 못하고 제자리에서 계속 회전하는 현상이 발생했다.

**원인**

두 가지 원인이 복합적으로 작용했다.

1. **카메라 각도 이탈**: 학습 데이터 수집 시의 로봇팔 위치와 물체를 든 상태에서의 위치가 달랐다. 파지 동작으로 로봇팔이 올라오면서 카메라 시야가 라인에서 벗어났다.
2. **CSI 카메라 버퍼 누적**: 작업 모드(`align_and_pick`) 실행 중 CSI 카메라 루프는 계속 돌면서 낡은 프레임이 버퍼에 쌓였다. 라인 트레이싱 재개 직후 이 오래된 프레임으로 조향 추론이 이루어져 잘못된 방향으로 회전했다.

**해결**

작업 완료 후 두 가지 복구 동작을 순서대로 수행:

```python
# jetson.ipynb — execute_work_logic() 이후 메인 루프
execute_work_logic(current_task_type, curr_dest_name)

flush_camera(10)  # ★★★ 여기서 CSI 카메라 버퍼 왕창 비움 (중요) ★★★
```

```python
def flush_camera(n=5):
    for _ in range(n):
        _ = camera.value   # 오래된 프레임 소진
        time.sleep(0.01)
```

```python
def reset_servos(self):
    TTLServo.servoAngleCtrl(5, 50, 1, 100)  # 카메라 주행 각도로 복귀
    # ... 나머지 서보 원위치
```

동작 시퀀스:

```
물체 집기 → 이동 → 물체 내려놓기
  → reset_servos() (카메라 주행 각도 복귀)
  → flush_camera(10) (CSI 버퍼 클리어)
  → 라인 트레이싱 재개
```

---

## 4. WiFi 환경에서 MQTT 메시지 유실

**증상**

WiFi 환경에서 간헐적으로 MQTT 메시지가 유실되어 로봇 상태가 대시보드에 반영되지 않거나 명령이 전달되지 않는 경우가 발생했다.

**원인**

- 기본 **QoS 0**(at most once) 설정으로 메시지 전달 보장 없음
- 네트워크 불안정 시 연결이 끊겨도 자동 재연결 로직 부재

**해결**

토픽 특성에 따라 QoS를 차등 적용:

| 토픽 | QoS | 이유 |
|------|-----|------|
| `robot/{id}/status` | 0 | 빈번한 상태 갱신 — 1건 유실해도 다음 프레임으로 보완 |
| `/robot/{id}/cmd` | 1 | 명령 누락 시 동작 오류 → 최소 1회 전달 보장 필요 |
| `cmd/{id}/request` | 1 | 동일 |

추가로 클라이언트별 재연결 처리:

- **Jetson / Qt HMI (paho-mqtt)**: `connect_async` + `loop_start` 방식으로 비동기 연결 유지, `on_disconnect` 콜백에서 재연결 트리거
- **Node-RED**: MQTT 브로커 노드의 reconnect 옵션 활성화

---

## 5. 카메라 자원 점유 충돌 — CSI·USB 웹캠 분리

**증상**

하나의 카메라로 라인 트레이싱(ResNet-18)과 객체 검출(YOLOv5s TFLite)을 모두 처리하려 했으나, 두 기능을 동시에 정상 동작시킬 수 없었다.

**원인**

Linux V4L2(Video4Linux2) 드라이버는 하나의 카메라 장치(`/dev/video0`)를 한 번에 하나의 프로세스/핸들만 점유하도록 제한한다. JetBot의 `Camera` 클래스는 GStreamer 파이프라인을 통해 CSI 카메라를 **프로그램 시작부터 상시 독점**하므로, 같은 장치를 `cv2.VideoCapture(0)`으로 다시 열면 열리지 않거나 충돌했다.

```python
camera = Camera()   # GStreamer가 CSI 카메라(/dev/video0)를 exclusive open
# ...
cap = cv2.VideoCapture(0)   # 이미 점유된 장치 → 실패
cap.isOpened()  # False
```

**해결**

용도별로 카메라 하드웨어를 분리:

| 역할 | 카메라 | 접근 방식 |
|------|--------|-----------|
| 라인 트레이싱 (ResNet-18) | CSI 카메라 | `Camera()` — GStreamer 파이프라인, 상시 점유 |
| 객체 검출 (YOLOv5s TFLite) | USB 웹캠 | `cv2.VideoCapture(1)` — 온디맨드 오픈/클로즈 |

```python
# ★ [핵심] 필요할 때만 열고 닫는 함수
def open_usb_camera(self):
    cap = cv2.VideoCapture(1)       # USB 웹캠 (/dev/video1)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)   # fallback
    return cap

def align_and_pick(self, target_label):
    cap = self.open_usb_camera()    # 작업 시작 시에만 오픈
    try:
        # YOLOv5s TFLite 추론 루프
        ...
    finally:
        cap.release()               # 작업 완료 후 즉시 반납
```

USB 웹캠은 작업 모드(`align_and_pick`) 진입 시에만 열고 완료 즉시 닫는다. 작업 종료 후에는 CSI 카메라 버퍼에 누적된 낡은 프레임을 비워 라인 트레이싱 재개 시 오추론을 방지한다([이슈 #3](#3-pick--place-후-라인-트레이싱-실패-빙글빙글) 참고):

```python
flush_camera(10)  # ★★★ CSI 카메라 버퍼 왕창 비움 (중요) ★★★
```

---

## 6. 카메라 실시간 스트림 + YOLO 동시 처리 시 UI 렉

**증상**

Qt HMI에서 카메라 실시간 스트림 송출과 YOLO TFLite 추론을 메인 스레드에서 함께 처리하면 UI가 멈추거나 응답이 느려졌다.

**원인**

영상 캡처와 딥러닝 추론은 CPU 집약적 작업이다. PySide6 이벤트 루프는 단일 메인 스레드에서 동작하므로, 동기 방식으로 프레임 캡처 → TFLite 추론 → UI 렌더링을 순차 처리하면 각 프레임마다 수십~수백 ms의 블로킹이 발생한다.

**해결**

PySide6 `QThread`로 워커를 분리하고 시그널/슬롯으로 결과를 UI에 전달:

```python
# Qt/utils/camera_worker.py
class CameraWorker(QThread):
    frame_ready = Signal(np.ndarray)

    def run(self):
        cap = cv2.VideoCapture(0)
        while self._running:
            ret, frame = cap.read()
            if ret:
                self.frame_ready.emit(frame)  # 메인 스레드 비침범
```

```python
# Qt/utils/yolo_tflite_worker.py
class YoloTfliteWorker(QThread):
    result_ready = Signal(list)  # 검출 결과 리스트

    def run(self):
        while self._running:
            if self._frame is not None:
                detections = self._infer(self._frame)
                self.result_ready.emit(detections)
```

```
메인 스레드 (UI 이벤트 루프)
  ├── CameraWorker (QThread) ──frame_ready──▶ UI 프레임 업데이트
  └── YoloTfliteWorker (QThread) ──result_ready──▶ 바운딩 박스 오버레이
```

각 워커가 독립 스레드에서 동작하므로 메인 스레드 블로킹 없이 실시간 스트림과 추론을 동시 처리.
