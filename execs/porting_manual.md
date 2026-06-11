# 보미 — Porting Manual

## 목차

1. [개발 환경](#1-개발-환경)
2. [외부 서비스 설정](#2-외부-서비스-설정)
3. [AGV 설정 (Jetson Nano)](#3-agv-설정-jetson-nano)
4. [MQTT 브로커 설정](#4-mqtt-브로커-설정)
5. [Node-RED 설정](#5-node-red-설정)
6. [Web Dashboard 빌드 및 배포](#6-web-dashboard-빌드-및-배포)
7. [Qt HMI 설정 (Raspberry Pi 5)](#7-qt-hmi-설정-raspberry-pi-5)
8. [실행 순서](#8-실행-순서)

---

## 1. 개발 환경

### 공통

| 항목 | 버전 |
|------|------|
| Python | 3.10 이상 |
| Node.js | 20.19.0 이상 또는 22.12.0 이상 |
| Node-RED | 최신 안정 버전 |
| Mosquitto | 2.x |

### 하드웨어별 OS

| 장치 | OS |
|------|----|
| 서버 (MQTT Broker / Node-RED) | Ubuntu 22.04 LTS 권장 |
| Raspberry Pi 5 (HMI) | Raspberry Pi OS (64-bit) |
| NVIDIA Jetson Nano | JetPack 4.6 |

---

## 2. 외부 서비스 설정

### 2.1 Firebase

1. [Firebase Console](https://console.firebase.google.com)에서 프로젝트 생성
2. **Firestore Database** 활성화 (프로덕션 모드)
3. **서비스 계정 키** 발급
   - 프로젝트 설정 → 서비스 계정 → 새 비공개 키 생성
   - 다운로드한 JSON 파일을 `Qt/assets/secrets/ssafy_embedded_qt-gui-controller.json`에 배치

### Firestore 컬렉션 구조

| 컬렉션 | 설명 |
|--------|------|
| `robots` | 로봇 상태 (robot_id, state, battery, pose 등) |
| `tasks` | 작업 이력 (type, destination, status 등) |
| `events` | 이벤트 로그 (obstacle_detected, task_done 등) |
| `interactions` | 사용자 명령 이력 (input_mode, parsed_type 등) |

### 2.2 OpenAI API (GMS 프록시)

Node-RED에서 GPT-4.1 nano(의도 파악), Whisper(STT), GPT-5(로그 분석)를 사용합니다.

- SSAFY GMS 프록시 엔드포인트: `https://gms.ssafy.io/gmsapi/api.openai.com/v1/`
- Node-RED 글로벌 변수 `GMS_KEY`에 Bearer 토큰 설정 (아래 Node-RED 설정 참고)

### 2.3 Telegram Bot

1. [@BotFather](https://t.me/botfather)에서 봇 생성 → Bot Token 발급
2. Node-RED에서 Telegram 노드에 토큰 설정

---

## 3. AGV 설정 (Jetson Nano)

### 실행 환경

- JetPack 4.6 (Python 3.6+ 포함)
- PyTorch (JetPack 번들 버전)
- OpenCV

### 실행

Jetson에서 Jupyter Notebook 서버 실행 후 노트북 열기:

```bash
jupyter notebook Jetson/jetson.ipynb
```

노트북 내 셀을 순서대로 실행:
1. 라이브러리 임포트 및 모델 로드
2. MQTT 연결 설정 (브로커 IP, robot_id 확인)
3. ResNet-18 라인 트레이싱 루프 시작

---

## 4. MQTT 브로커 설정

### Mosquitto 설치

```bash
sudo apt-get update
sudo apt-get install -y mosquitto mosquitto-clients
```

### 설정 파일 (`/etc/mosquitto/mosquitto.conf`)

```conf
listener 1883
allow_anonymous true
```

### 실행

```bash
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

> **브로커 주소**: `10.41.145.221`, **포트**: `1883`  
> 환경에 따라 `Qt/config.py`의 `mqtt_host` 수정 필요

---

## 5. Node-RED 설정

### 설치

```bash
npm install -g --unsafe-perm node-red
```

### 필요 노드 설치

Node-RED 실행 후 팔레트 관리에서 설치:

```
node-red-contrib-firebase-admin
node-red-contrib-telegrambot
```

### 플로우 임포트

1. `node-red` 실행 → `http://localhost:1880` 접속
2. 우상단 메뉴 → **Import** → `Node_red_flow/flows.json` 파일 선택

### 환경 변수 설정

Node-RED 우상단 메뉴 → **설정** → **환경 변수** 탭에서 아래 항목 추가:

| 변수명 | 값 | 설명 |
|--------|----|------|
| `GMS_KEY` | `Bearer sk-...` | OpenAI/GMS API 키 |

### Firebase Admin 초기화

플로우 내 **Init Firestore** 함수 노드에서 서비스 계정 키 경로를 환경에 맞게 수정합니다.

---

## 6. Web Dashboard 빌드 및 배포

### 개발 서버 실행

```bash
cd Agv_dashboard
npm install
npm run dev
# → http://localhost:5173
```

### 프로덕션 빌드

```bash
npm run build
# dist/ 폴더 생성
```

### Node-RED API 주소 설정

`Agv_dashboard/src/config/` 아래 설정 파일에서 Node-RED 서버 주소를 환경에 맞게 변경합니다.

---

## 7. Qt HMI 설정 (Raspberry Pi 5)

### Python 의존성 설치

```bash
cd Qt
pip install -r requirements.txt
```

**requirements.txt**

```
PySide6
paho-mqtt
firebase-admin
pytz
opencv-python
pyqtgraph
numpy
```

### 환경 설정

`Qt/config.py`에서 아래 항목 수정:

```python
mqtt_host: str = "10.41.145.221"   # MQTT 브로커 IP
mqtt_port: int = 1883
robot_id: str = "agv1"
```

### Firebase 서비스 계정 키 배치

```
Qt/assets/secrets/ssafy_embedded_qt-gui-controller.json
```

### UI 파일 컴파일 (변경 시에만)

```bash
python tools/compile_ui.py
```

### 실행

```bash
python mainwindow.py
```

---

## 8. 실행 순서

전체 시스템을 올바르게 구동하려면 아래 순서를 따릅니다.

| 순서 | 구성 요소 | 실행 위치 |
|------|-----------|-----------|
| 1 | Mosquitto MQTT 브로커 | 서버 |
| 2 | Node-RED | 서버 |
| 3 | Web Dashboard (선택) | 서버 또는 로컬 |
| 4 | Jetson Nano AGV | AGV (Jetson) |
| 5 | Qt HMI | Raspberry Pi 5 |

> MQTT 브로커와 Node-RED가 먼저 실행되어야 Jetson과 Qt HMI의 MQTT 연결이 정상적으로 수립됩니다.
