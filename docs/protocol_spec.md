# 보미 통신 명세

## 목차

1. [공통 원칙](#1-공통-원칙)
2. [프로토콜 매트릭스](#2-프로토콜-매트릭스)
3. [MQTT 명세](#3-mqtt-명세)
4. [REST API 명세](#4-rest-api-명세)
5. [Firestore 스키마](#5-firestore-스키마)

---

## 1. 공통 원칙

| 항목 | 규격 |
|------|------|
| 데이터 포맷 | JSON (UTF-8) |
| 필드 네이밍 | snake_case |
| 타임스탬프 | Unix milliseconds (`ts`, `created_at`, `updated_at`) |
| Robot ID | `agv1` (단일 로봇 운영) |
| MQTT Broker | Mosquitto — host `10.41.145.221`, port `1883` |
| Node-RED API | host `10.41.145.221`, port `1880` |

---

## 2. 프로토콜 매트릭스

| 방향 | 프로토콜 | 브로커/서버 | 목적 |
|------|----------|-------------|------|
| Jetson → Node-RED | MQTT | Mosquitto | 로봇 상태, YOLO 추론 결과 전송 |
| Raspberry Pi HMI → Node-RED | MQTT | Mosquitto | 제어 명령, 작업 요청 전송 |
| Node-RED → Raspberry Pi HMI | MQTT | Mosquitto | 상태, 태스크, 추론 결과 수신 |
| Web Dashboard → Node-RED | REST (HTTP GET) | Node-RED | 로봇/태스크/이벤트 조회 |
| Node-RED → Firebase | Firestore SDK | Firebase | 상태, 태스크, 이벤트, 인터랙션 저장 |
| Node-RED → OpenAI | HTTP POST | GMS Proxy | Whisper STT, GPT-4.1 nano, GPT-5 호출 |
| Node-RED ↔ Telegram | Bot API | Telegram | 사용자 명령 수신, 작업 진행 알림 |

---

## 3. MQTT 명세

### 3.1 토픽 일람

| 토픽 | 방향 | 발행자 | 구독자 | 목적 |
|------|------|--------|--------|------|
| `robot/{robot_id}/status` | pub | Jetson | Node-RED | 로봇 상태 스트림 |
| `robot/{robot_id}/task` | pub | Node-RED | Jetson | 작업 할당 |
| `/robot/{robot_id}/cmd` | pub | Qt HMI | Jetson | 수동 제어 명령 |
| `/robot/{robot_id}/status/#` | pub | Jetson | Qt HMI | 로봇 상태 세부 정보 |
| `/robot/{robot_id}/inference/yolo` | pub | Jetson | Qt HMI | YOLO 추론 결과 |
| `cmd/{robot_id}/request` | pub | Qt HMI, Telegram | Node-RED | 명령 요청 |
| `telemetry/#` | pub | Jetson | Qt HMI | 텔레메트리 데이터 |

> `{robot_id}` = `agv1`

---

### 3.2 `robot/{robot_id}/status`

**Jetson → Node-RED**
로봇의 현재 상태를 주기적으로 발행합니다. Node-RED는 이 토픽을 기반으로 Firestore `robots` 컬렉션을 갱신합니다.

**페이로드**

| 필드 | 타입 | 설명 |
|------|------|------|
| `robot_id` | string | 로봇 식별자 (`agv1`) |
| `state` | string | 로봇 상태 (`idle`, `running`, `charging`, `error`) |
| `task_id` | string \| null | 현재 실행 중인 태스크 ID |
| `battery` | number | 배터리 잔량 (0~100, %) |
| `pose` | object | 현재 위치 (`x`, `y`, `heading`) |
| `ts` | number | Unix milliseconds |

```json
{
  "robot_id": "agv1",
  "state": "running",
  "task_id": "task_20250101_001",
  "battery": 82,
  "pose": { "x": 42.0, "y": 70.0, "heading": 90 },
  "ts": 1735689600000
}
```

---

### 3.3 `robot/{robot_id}/task`

**Node-RED → Jetson**
Node-RED가 태스크를 분기하여 Jetson에 전달하는 작업 명령 토픽입니다.

**페이로드**

| 필드 | 타입 | 설명 |
|------|------|------|
| `task_id` | string | 태스크 고유 ID |
| `type` | string | 작업 유형 (`deliver_water`, `collect_cup`, `go_home` 등) |
| `destination` | string | 목적지 POI 이름 (`Room_A`, `Water`, `Basket` 등) |
| `payload` | object \| null | 작업별 추가 데이터 |
| `created_at` | number | Unix milliseconds |

```json
{
  "task_id": "task_20250101_001",
  "type": "deliver_water",
  "destination": "Room_A",
  "payload": null,
  "created_at": 1735689600000
}
```

**POI 목록**

| POI | 설명 |
|-----|------|
| `Charger` | 충전 스테이션 |
| `Water` | 물 보충 장소 |
| `Basket` | 수거 바구니 |
| `Room_A` | 입실자 A 방 |
| `Room_B` | 입실자 B 방 |
| `Room_C` | 입실자 C 방 |

---

### 3.4 `/robot/{robot_id}/cmd`

**Qt HMI → Jetson**
웹 대시보드 또는 HMI에서 수동 제어 명령을 전송할 때 사용합니다.

**페이로드**

| 필드 | 타입 | 설명 |
|------|------|------|
| `mode` | string | 제어 모드 (`move`, `stop`, `rotate` 등) |
| `direction` | string \| null | 이동 방향 (`forward`, `backward`, `left`, `right`) |
| `value` | any | 모드별 추가 값 |
| `speed` | number | 속도 비율 (0.0 ~ 1.0) |
| `ts` | number | Unix milliseconds |

```json
{
  "mode": "move",
  "direction": "forward",
  "value": "forward",
  "speed": 0.5,
  "ts": 1735689600000
}
```

---

### 3.5 `/robot/{robot_id}/status/#`

**Jetson → Qt HMI**
로봇 상태 세부 항목을 서브토픽으로 분리하여 발행합니다.

| 서브토픽 예시 | 내용 |
|--------------|------|
| `/robot/agv1/status/pose` | 현재 위치 (`x`, `y`, `heading`) |
| `/robot/agv1/status/battery` | 배터리 잔량 |
| `/robot/agv1/status/state` | 로봇 상태 문자열 |

```json
{ "x": 42.0, "y": 70.0, "heading": 90 }
```

---

### 3.6 `/robot/{robot_id}/inference/yolo`

**Jetson → Qt HMI**
YOLOv5s TFLite 모델의 객체 감지 결과를 실시간으로 전송합니다. Qt HMI는 이 결과를 오버레이로 표시합니다.

**페이로드** — 검출된 객체 배열

| 필드 | 타입 | 설명 |
|------|------|------|
| `box` | number[] | 바운딩 박스 `[x, y, w, h]` (픽셀) |
| `cls` | number | 클래스 ID (0: Cup, 1: Doll, 2: Block) |
| `conf` | number | 신뢰도 (0.0 ~ 1.0) |

```json
[
  { "box": [120, 80, 60, 90], "cls": 0, "conf": 0.87 },
  { "box": [300, 150, 55, 80], "cls": 2, "conf": 0.72 }
]
```

**클래스 정의**

| cls | 이름 | 설명 |
|-----|------|------|
| 0 | Cup | 컵 |
| 1 | Doll | 인형 |
| 2 | Block | 블록 |

---

### 3.7 `cmd/{robot_id}/request`

**Qt HMI / Telegram → Node-RED**
HMI 또는 Telegram WebApp에서 작업을 요청할 때 사용합니다. Node-RED는 이 요청을 태스크로 변환하여 Jetson에 전달하거나 Firebase에 기록합니다.

**페이로드**

| 필드 | 타입 | 설명 |
|------|------|------|
| `type` | string | 요청 유형 (`deliver_water`, `collect_cup`, `go_home` 등) |
| `destination` | string \| null | 목적지 POI |
| `source` | string | 요청 출처 (`hmi_qt`, `telegram`) |
| `user_id` | string | 요청자 ID |
| `input_mode` | string | 입력 방식 (`button`, `text`, `voice`) |
| `ts` | number | Unix milliseconds |

```json
{
  "type": "deliver_water",
  "destination": "Room_B",
  "source": "hmi_qt",
  "user_id": "rpi_hmi_01",
  "input_mode": "voice",
  "ts": 1735689600000
}
```

---

### 3.8 `telemetry/#`

**Jetson → Qt HMI**
센서 및 시스템 텔레메트리 데이터를 서브토픽으로 구분하여 발행합니다.

| 서브토픽 예시 | 내용 |
|--------------|------|
| `telemetry/agv1/motor` | 모터 PWM, 전류 |
| `telemetry/agv1/imu` | 가속도, 각속도 |

---

## 4. REST API 명세

Node-RED가 `10.41.145.221:1880`에서 제공하는 HTTP REST API입니다.
모든 응답은 `Content-Type: application/json`입니다.

---

### 4.1 `GET /api/robots`

로봇 목록 및 현재 상태를 조회합니다.

**Query Parameters**

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `limit` | number | 100 | 최대 조회 수 (최대 500) |

**Response**

```json
{
  "robots": [
    {
      "robot_id": "agv1",
      "state": "idle",
      "task_id": null,
      "battery": 95,
      "pose": { "x": 5.0, "y": 1.0, "heading": 0 },
      "updated_at": 1735689600000
    }
  ]
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `robot_id` | string | 로봇 ID |
| `state` | string | `idle`, `running`, `charging`, `error` |
| `task_id` | string \| null | 현재 태스크 ID |
| `battery` | number | 배터리 % |
| `pose` | object | 현재 위치 |
| `updated_at` | number | 마지막 갱신 시각 (ms) |

---

### 4.2 `GET /api/tasks`

태스크 목록을 조회합니다.

**Query Parameters**

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `status` | string | — | 필터: `pending`, `running`, `done`, `failed` |
| `limit` | number | 50 | 최대 조회 수 (최대 500) |

**Response**

```json
{
  "tasks": [
    {
      "task_id": "task_20250101_001",
      "type": "deliver_water",
      "destination": "Room_A",
      "status": "done",
      "robot_id": "agv1",
      "created_at": 1735689600000,
      "updated_at": 1735689900000
    }
  ]
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `task_id` | string | 태스크 ID |
| `type` | string | 작업 유형 |
| `destination` | string | 목적지 POI |
| `status` | string | `pending`, `running`, `done`, `failed` |
| `robot_id` | string | 담당 로봇 |
| `created_at` | number | 생성 시각 (ms) |
| `updated_at` | number | 최종 갱신 시각 (ms) |

---

### 4.3 `GET /api/interactions`

사용자 인터랙션(명령) 로그를 조회합니다.

**Query Parameters**

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `limit` | number | 100 | 최대 조회 수 (최대 500) |
| `type` | string | — | 작업 유형 필터 (`deliver_water` 등) |
| `input_mode` | string | — | 입력 방식 필터 (`voice`, `text`, `button`) |
| `result` | string | — | 결과 필터 (`accepted`, `rejected`, `pending`) |

**Response**

```json
{
  "interactions": [
    {
      "interaction_id": "itx_1735689600000",
      "source": "hmi_qt",
      "user_id": "rpi_hmi_01",
      "input_mode": "voice",
      "raw_input": "Room A에 물 가져다줘",
      "parsed_type": "deliver_water",
      "destination": "Room_A",
      "result": "accepted",
      "task_id": "task_20250101_001",
      "created_at": 1735689600000
    }
  ]
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `interaction_id` | string | 인터랙션 ID |
| `source` | string | 요청 출처 (`hmi_qt`, `telegram`) |
| `user_id` | string | 요청자 ID |
| `input_mode` | string | 입력 방식 |
| `raw_input` | string | 원본 입력 텍스트 |
| `parsed_type` | string | LLM이 파악한 작업 유형 |
| `destination` | string | 목적지 |
| `result` | string | `accepted`, `rejected`, `pending` |
| `task_id` | string \| null | 생성된 태스크 ID |
| `created_at` | number | 생성 시각 (ms) |

---

### 4.4 `GET /api/interactions/insight`

Firestore의 인터랙션 로그를 GPT-5가 분석하여 운영 인사이트를 반환합니다.

**Query Parameters**

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `range` | string | `week` | 분석 기간 (`day`, `week`) |

**Response**

```json
{
  "range": "week",
  "cached": false,
  "generated_at": 1735689600000,
  "ttl_ms": 180000,
  "insight": {
    "summary": "이번 주 총 42건의 작업 중 Room_A 물 전달 요청이 가장 많았습니다.",
    "insights": [
      {
        "category": "usage_pattern",
        "description": "오전 10시~11시에 물 전달 요청 집중",
        "severity": "info"
      }
    ],
    "actions": [
      {
        "priority": 1,
        "description": "오전 루틴에 Room_A, Room_B 순차 물 전달 스케줄 추가 검토"
      }
    ]
  }
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `range` | string | 분석 기간 |
| `cached` | boolean | 캐시 히트 여부 |
| `generated_at` | number | 인사이트 생성 시각 (ms) |
| `ttl_ms` | number | 캐시 유효 시간 (ms) |
| `insight.summary` | string | 종합 요약 |
| `insight.insights` | array | 이상 징후, 패턴 목록 |
| `insight.actions` | array | 우선순위별 조치 제안 |

---

### 4.5 기타 API

| 엔드포인트 | 설명 |
|-----------|------|
| `GET /api/events` | 이벤트 로그 조회 |
| `GET /api/summary` | 로봇/태스크 집계 현황 |
| `GET /api/user/brief` | 오늘의 업무 요약 브리핑 |
| `GET /api/user/summary` | 사용자별 인터랙션 통계 |
| `GET /api/app/settings` | 앱 설정 조회 |
| `POST /api/app/settings` | 앱 설정 변경 |

---

## 5. Firestore 스키마

Firebase Firestore를 공용 데이터베이스로 사용합니다. Node-RED와 Qt HMI 양쪽에서 읽고 씁니다.

### 5.1 `robots` 컬렉션

문서 ID: `{robot_id}` (예: `agv1`)

| 필드 | 타입 | 설명 |
|------|------|------|
| `robot_id` | string | 로봇 ID |
| `state` | string | 현재 상태 |
| `task_id` | string \| null | 수행 중인 태스크 ID |
| `battery` | number | 배터리 % |
| `pose` | map | `{x, y, heading}` |
| `updated_at` | number | 마지막 갱신 ms |

---

### 5.2 `tasks` 컬렉션

문서 ID: `{task_id}`

| 필드 | 타입 | 설명 |
|------|------|------|
| `task_id` | string | 태스크 ID |
| `type` | string | 작업 유형 |
| `destination` | string | 목적지 POI |
| `status` | string | `pending`, `running`, `done`, `failed` |
| `robot_id` | string \| null | 담당 로봇 |
| `created_at` | number | 생성 ms |
| `updated_at` | number | 갱신 ms |

---

### 5.3 `events` 컬렉션

문서 ID: 자동 생성

| 필드 | 타입 | 설명 |
|------|------|------|
| `event_id` | string | 이벤트 ID |
| `robot_id` | string | 관련 로봇 |
| `type` | string | 이벤트 유형 (`obstacle_detected`, `task_done`, `low_battery` 등) |
| `detail` | map | 이벤트 상세 데이터 |
| `ts` | number | 발생 시각 ms |

---

### 5.4 `interactions` 컬렉션

문서 ID: `{interaction_id}`

| 필드 | 타입 | 설명 |
|------|------|------|
| `interaction_id` | string | 인터랙션 ID |
| `source` | string | 출처 (`hmi_qt`, `telegram`) |
| `user_id` | string | 요청자 ID |
| `input_mode` | string | `button`, `text`, `voice` |
| `raw_input` | string | 원본 입력 |
| `parsed_type` | string | 파악된 작업 유형 |
| `destination` | string | 목적지 |
| `result` | string | `accepted`, `rejected`, `pending` |
| `task_id` | string \| null | 생성 태스크 ID |
| `created_at` | number | 생성 ms |
| `updated_at` | number | 갱신 ms |
