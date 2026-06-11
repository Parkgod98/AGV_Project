<div align="center">

<img src="docs/images/logo.png" alt="보미 Logo" width="180"/>

# 🤖 보미

요양보호사의 든든한 AI 로봇 동료

**LLM 및 Digital Twin 기반의 스마트 요양 시설 AGV 솔루션**

자연어 명령 인식부터 일일 업무 자동 리포팅까지, 빈틈없는 올인원 케어

<br/>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-41CD52?style=flat-square&logo=qt&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D?style=flat-square&logo=vue.js&logoColor=white)
![Node-RED](https://img.shields.io/badge/Node--RED-8F0000?style=flat-square&logo=nodered&logoColor=white)
![MQTT](https://img.shields.io/badge/MQTT-3C5280?style=flat-square&logo=eclipsemosquitto&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=flat-square&logo=firebase&logoColor=black)
![OpenAI](https://img.shields.io/badge/OpenAI_GPT-412991?style=flat-square&logo=openai&logoColor=white)
![Jetson](https://img.shields.io/badge/NVIDIA_Jetson-76B900?style=flat-square&logo=nvidia&logoColor=white)

[아키텍처](#-2-system-architecture), [기술 스택](#-3-tech-stack), [시작하기](#-4-getting-started), [프로젝트 구조](#-5-project-structure), [팀](#-6-contributors)

</div>

---

## 📑 Table of Contents

1. [Background](#-1-background)
2. [System Architecture](#-2-system-architecture)
3. [Tech Stack](#-3-tech-stack)
4. [Getting Started](#-4-getting-started)
5. [Project Structure](#-5-project-structure)
6. [Contributors](#-6-contributors)

---

## 🔍 1. Background

요양원에서는 물 전달, 물품 수거 같은 간단한 반복 요청이 하루에도 수십 번 발생하여 요양보호사의 핵심 케어 시간이 줄어들고, 바닥에 방치된 물품으로 낙상 위험이 증가합니다.

| 문제 | 해결 방법 |
|------|-----------|
| 반복 심부름으로 요양보호사 핵심 케어 시간 감소 | AGV가 물 전달, 수거, 정리 등 단순 반복 업무 대행 |
| 버튼 중심 UI의 상황별 명령 표현 한계 | 터치, 텍스트, 음성(Whisper) 멀티모달 명령 입력 지원 |
| 바닥 방치물 및 장애물로 인한 낙상 위험 | YOLOv5s 실시간 객체 감지 → 즉시 정지, 회피 |
| 복잡한 경로(곡선, 교차로) 주행 불안정 | ResNet-18 딥러닝 라인 트레이싱으로 정밀 주행 |
| 원격지 로봇 상태, 진행 상황 파악 어려움 | MQTT 디지털 트윈 + Telegram WebApp 실시간 모니터링 |
| 장애/오류 로그를 운영자가 수동으로 분석 | GPT-5 기반 로그 자동 요약 및 유지보수 인사이트 제공 |

---

## 🏗 2. System Architecture

```text
         NVIDIA Jetson Nano (AGV)              Raspberry Pi 5 (HMI)
  ┌────────────────────────────────┐      ┌──────────────────────────┐
  │  ResNet-18  │  YOLOv5s TFLite │      │  PySide6 Qt GUI          │
  │  라인 트레이싱   객체 인식      │      │  터치, 텍스트, 음성 명령  │
  │  [주행 모드] 웹캠 OFF           │      │  Whisper STT → GPT 의도  │
  │  [작업 모드] 웹캠 ON + 로봇팔   │      │  실시간 상태, 로그 시각화  │
  └────────────────────────────────┘      └──────────────────────────┘
              │  MQTT pub                            │  MQTT sub/pub
              └──────────────────┬───────────────────┘
                                 ▼
               ┌──────────────────────────────────────┐
               │           Node-RED Server             │
               │  MQTT 수신, 태스크 분기, API 정의     │
               │  Firebase 상태 관리, LLM 호출         │
               └──────────┬─────────────┬─────────────┘
                          │             │
             REST/WebSocket│             │ Firestore
                          ▼             ▼
             ┌─────────────────┐  ┌──────────────────┐
             │  Web Dashboard  │  │  Firebase DB      │
             │  Vue 3 + Vite   │  │  작업 로그, 이벤트│
             │  실시간 관제 맵  │  └──────────────────┘
             └─────────────────┘
                                   Telegram WebApp
                                   실시간 진행 알림
```

### 동작 시나리오

| 단계 | 동작 | 기술 |
|------|------|------|
| **① 명령 수신** | 버튼, 텍스트, 음성으로 작업 요청 | Whisper(STT) + GPT-4.1 nano(의도 파악) |
| **② 경로 주행** | 디지털 트윈 기반 최적 경로 주행 및 정밀 회전 | ResNet-18, 조향 regression |
| **③ Pick & Place** | 목적지 도착 후 객체 인식 및 로봇팔 제어 | YOLOv5s TFLite (Cup / Doll / Block) |
| **④ 실시간 보고** | 작업 진행 상황 즉시 전달 | Telegram Bot API, MQTT |

### 주요 기능

| 기능 | 설명 |
|------|------|
| **멀티모달 명령** | 터치, 텍스트, 음성 3가지 입력 방식 지원, Whisper + GPT-4.1 nano 의도 해석 |
| **자율 주행** | ResNet-18 라인 트레이싱, 곡선, 교차로, 180° 정밀 회전 구현 |
| **온디맨드 리소스 최적화** | 주행 중 웹캠 OFF(ResNet18), 작업 시 웹캠 ON(YOLOv5s) 모드 자동 전환 |
| **Pick & Place** | YOLOv5s 객체 인식(컵, 인형, 블록) 후 로봇팔 파지, 전달, 정리 수행 |
| **디지털 트윈** | MQTT로 로봇 위치, 상태를 Vue3 웹 맵에 실시간 동기화 |
| **LLM 운영 브리핑** | GPT-5가 Firestore 로그 분석 → 이상 징후, 원인 후보, 조치 순서 제안 |
| **원격 제어** | 비상 상황 발생 시 웹 대시보드에서 즉시 수동 개입 |

---

## 🧰 3. Tech Stack

| 영역 | 기술 |
|------|------|
| **Robot AI (Edge)** | ![Jetson](https://img.shields.io/badge/NVIDIA_Jetson_Nano-76B900?style=flat-square&logo=nvidia&logoColor=white) ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white) ![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white) ResNet-18, YOLOv5s TFLite |
| **HMI (현장 디스플레이)** | ![Raspberry Pi](https://img.shields.io/badge/Raspberry_Pi_5-A22846?style=flat-square&logo=raspberrypi&logoColor=white) ![PySide6](https://img.shields.io/badge/PySide6-41CD52?style=flat-square&logo=qt&logoColor=white) pyqtgraph, paho-mqtt, firebase-admin |
| **AI / LLM** | ![OpenAI](https://img.shields.io/badge/GPT--4.1_nano-412991?style=flat-square&logo=openai&logoColor=white) ![OpenAI](https://img.shields.io/badge/GPT--5-412991?style=flat-square&logo=openai&logoColor=white) ![Whisper](https://img.shields.io/badge/Whisper_STT-412991?style=flat-square&logo=openai&logoColor=white) |
| **Orchestration** | ![Node-RED](https://img.shields.io/badge/Node--RED-8F0000?style=flat-square&logo=nodered&logoColor=white) ![MQTT](https://img.shields.io/badge/Mosquitto-3C5280?style=flat-square&logo=eclipsemosquitto&logoColor=white) ![Firebase](https://img.shields.io/badge/Firebase_Firestore-FFCA28?style=flat-square&logo=firebase&logoColor=black) |
| **Web Dashboard** | ![Vue.js](https://img.shields.io/badge/Vue.js_3-4FC08D?style=flat-square&logo=vue.js&logoColor=white) ![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white) ![Pinia](https://img.shields.io/badge/Pinia-F1B739?style=flat-square&logo=pinia&logoColor=black) Axios, Vue Router |
| **알림** | ![Telegram](https://img.shields.io/badge/Telegram_Bot-26A5E4?style=flat-square&logo=telegram&logoColor=white) Telegram WebApp |

### 하드웨어 스펙

| 구분 | 항목 | 상세 사양 |
|------|------|-----------|
| **Main Robot** | AGV 모델 | JetBot v0.4.0 기반 커스텀 플랫폼 |
| **HMI Controller** | 메인 보드 | Raspberry Pi 5 (BCM2712 SoC) |
| **Edge AI** | AI 가속기 | NVIDIA Jetson Nano |
| **Vision** | 카메라 | CSI 카메라(주행용), USB 웹캠(객체인식용) |
| **Mechanics** | 구동부 | DC 모터 + 환경 정리용 로봇팔 |
| **Connectivity** | 무선 통신 | Wi-Fi (MQTT over TCP/IP) |

---

## 🚀 4. Getting Started

### 사전 요구사항

| 항목 | 버전 |
|------|------|
| Python | 3.10+ |
| Node.js | 20 LTS 이상 (22 권장) |
| Node-RED | 최신 안정 버전 |
| MQTT Broker | Mosquitto |

### 1) MQTT 브로커 & Node-RED 기동

```bash
# Mosquitto 브로커 실행
mosquitto -c /etc/mosquitto/mosquitto.conf

# Node-RED 실행 후 플로우 임포트
node-red
# → http://localhost:1880 접속
# agv_project/Node_red_flow/flows.json 가져오기(Import)
```

### 2) Qt HMI 실행 (Raspberry Pi 5)

```bash
cd agv_project/Qt

# 의존성 설치
pip install -r requirements.txt

# UI 파일 컴파일 (변경 시에만)
python tools/compile_ui.py

# 실행
python mainwindow.py
```

### 3) Web Dashboard 실행

```bash
cd agv_project/Agv_dashboard

npm install
npm run dev
# → http://localhost:5173
```

### 4) AGV Robot 실행 (Jetson Nano)

```bash
# Jetson에서 주피터 노트북 실행
jupyter notebook agv_project/Jetson/jetson.ipynb
```

> Firebase 서비스 계정 키(`serviceAccountKey.json`)는 별도 발급 후 `agv_project/Qt/assets/secrets/` 아래에 배치하세요.
> OpenAI API 키는 Node-RED 환경 변수 또는 Qt `config.py`에 설정하세요.

---

## 📂 5. Project Structure

```text
AGV_Project/
├── agv_project/
│   ├── Agv_dashboard/        # 웹 관제 대시보드 (Vue 3 + Vite)
│   │   └── src/
│   │       ├── components/   # DigitalTwinSection, MiniMap, AlertsPanel 등
│   │       ├── views/        # Home, Robots, Tasks, Events 화면
│   │       ├── api/          # REST 연동 모듈
│   │       └── stores/       # Pinia 상태 관리
│   │
│   ├── Qt/                   # 현장 HMI (PySide6, Raspberry Pi 5)
│   │   ├── pages/            # overview, map, tasks, logs, control, analytics
│   │   ├── utils/            # MQTT, Firestore, YOLO 추론, 카메라 워커
│   │   ├── models/           # best-fp16.tflite (YOLOv5s)
│   │   ├── assets/qss/       # 다크블루, 핑크 등 테마
│   │   └── mainwindow.py
│   │
│   ├── Jetson/               # AGV 자율주행 코드 (Jetson Nano)
│   │   └── jetson.ipynb      # ResNet-18 라인 트레이싱 + 모터 제어 + 로봇팔
│   │
│   ├── Node_red_flow/        # Node-RED 오케스트레이션
│   │   ├── flows.json        # 최신 플로우 (LLM 분기, Firebase, API 포함)
│   │   └── archive/          # 버전별 백업
│   │
│   └── Experiments/          # 프로토타입, 실험 노트북
│
└── README.md
```

---

## 👥 6. Contributors

| 이름 | 역할 | 담당 |
|------|------|------|
| 박현성 | 팀장 / EMB, AI, FULL | Jetson 자율주행(ResNet-18), Node-RED 플로우, LLM 연동, 관제 대시보드 |
| 장유진 | EMB, 제어, AI | AGV 로봇팔 제어, YOLOv5 학습 및 추론 연동, Raspberry Pi Qt 인터페이스 |

> 작성 기준: `git shortlog -sne --all` 및 발표 자료 기반 역할 분류.

---

<div align="center">

**스마트 요양시설 AGV 솔루션** | SSAFY 14기 임베디드 트랙 관통 프로젝트

</div>
