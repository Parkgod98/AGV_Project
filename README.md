# 🤖 Smart AGV Control System with Digital Twin
> **Qt 기반 자율주행 로봇(AGV)과 Vue.js 기반 실시간 관제 대시보드를 연동한 스마트 물류 시스템**

![Project Demo](path/to/demo.gif)
*(여기에 로봇이 움직이는 모습과 대시보드가 연동되는 움짤을 넣으면 최고입니다)*

## 📖 프로젝트 개요 (Overview)
이 프로젝트는 물류 현장에서 사용되는 **무인 운반차(AGV)** 시스템을 모사하여 구축했습니다.
**Raspberry Pi**와 **Camera**를 탑재한 로봇이 라인을 따라 자율 주행하며 장애물을 인식하고, **Web Dashboard**를 통해 실시간 위치 모니터링 및 원격 제어가 가능하도록 구현했습니다.

단순한 하드웨어 제어를 넘어, **Node-RED**를 오케스트레이터로 활용하여 **Edge(Robot) ↔ Server ↔ Client(Web)** 간의 유기적인 데이터 파이프라인을 구축하는 데 중점을 두었습니다.

## 🛠 기술 스택 (Tech Stack)

| 영역 | 기술 스택 |
| :--- | :--- |
| **Robot (Edge)** | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![PyQt5](https://img.shields.io/badge/PyQt5-41CD52?style=flat&logo=qt&logoColor=white) ![TensorFlow Lite](https://img.shields.io/badge/TFLite-FF6F00?style=flat&logo=tensorflow&logoColor=white) |
| **Server / Orchestration** | ![Node-RED](https://img.shields.io/badge/Node--RED-8F0000?style=flat&logo=nodered&logoColor=white) ![MQTT](https://img.shields.io/badge/MQTT-3C5280?style=flat&logo=eclipse-mosquitto&logoColor=white) ![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=flat&logo=firebase&logoColor=black) |
| **Dashboard (Client)** | ![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?style=flat&logo=vue.js&logoColor=white) ![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat&logo=vite&logoColor=white) |

## 🌟 핵심 기능 (Key Features)

### 1. 자율 주행 & 객체 인식 (Robot)
- **Line Tracing:** 바닥의 라인을 인식하여 정밀 주행 및 교차로 판단.
- **AI Vision:** `YOLOv5 (TFLite)` 모델을 활용하여 사람, 장애물 등 객체 실시간 탐지 및 회피/정지 로직 수행.
- **GUI Control:** `PyQt5` 기반의 터치스크린 UI로 현장에서 즉각적인 상태 확인 및 조작 가능.

### 2. 실시간 관제 시스템 (Dashboard)
- **Digital Twin:** 로봇의 물리적 위치를 웹 상의 맵에 실시간 동기화.
- **Remote Control:** 웹에서 목적지 설정 및 작업 명령(Task) 하달.
- **Monitoring:** 배터리 상태, 적재 여부, 센서 데이터 실시간 그래프 시각화.

### 3. 초저지연 데이터 통신
- **MQTT Protocol:** 로봇과 서버 간의 경량화된 메시징으로 지연 시간 최소화.
- **Node-RED Flows:** 복잡한 제어 로직과 데이터 흐름을 시각적으로 설계 및 관리.

## 🏗 시스템 아키텍처 (Architecture)

```mermaid
graph LR
    A[AGV Robot\n(PyQt + Vision)] <-->|MQTT| B(Node-RED\nServer);
    B <-->|WebSocket/HTTP| C[Web Dashboard\n(Vue.js)];
    B -->|Log Data| D[(Firebase DB)];