# 🤖 Smart AGV Control System with Digital Twin
> **Qt 기반 자율주행 로봇(AGV)과 Vue.js 기반 실시간 관제 대시보드를 연동한 스마트 물류 시스템**

![Project Demo Placeholder](https://via.placeholder.com/800x400?text=Upload+Your+Demo+Video+Here)


## 📖 프로젝트 개요 (Overview)
이 프로젝트는 물류 현장의 효율성을 높이기 위해 **자율주행 AGV(Automated Guided Vehicle)**와 **디지털 트윈(Digital Twin) 관제 시스템**을 구축했습니다.

**Raspberry Pi**와 **Camera**를 탑재한 로봇이 딥러닝(ResNet-18) 기반으로 라인을 따라 자율 주행하며, **Web Dashboard**를 통해 실시간 위치 모니터링 및 원격 제어가 가능하도록 구현했습니다. 단순한 하드웨어 제어를 넘어, **Node-RED**를 오케스트레이터로 활용하여 **Edge(Robot) ↔ Server ↔ Client(Web)** 간의 유기적인 데이터 파이프라인을 구축하는 데 중점을 두었습니다.

## 🛠 기술 스택 (Tech Stack)

| 영역 | 기술 스택 |
| :--- | :--- |
| **Robot (Edge)** | ![Jetson](https://img.shields.io/badge/NVIDIA_Jetson-76B900?style=flat&logo=nvidia&logoColor=white) ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white) ![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat&logo=opencv&logoColor=white) **ResNet-18** (Line Tracing), **YOLOv5** (Object Detection) |
| **HMI / Display** | ![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-A22846?style=flat&logo=raspberrypi&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![PySide6](https://img.shields.io/badge/PySide6-41CD52?style=flat&logo=qt&logoColor=white)  |
| **Server / Orchestration** | ![Node-RED](https://img.shields.io/badge/Node--RED-8F0000?style=flat&logo=nodered&logoColor=white) ![MQTT](https://img.shields.io/badge/MQTT-3C5280?style=flat&logo=eclipse-mosquitto&logoColor=white) ![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=flat&logo=firebase&logoColor=black) |
| **Dashboard (Web)** | ![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?style=flat&logo=vue.js&logoColor=white) ![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat&logo=vite&logoColor=white) ![Pinia](https://img.shields.io/badge/Pinia-F1B739?style=flat&logo=pinia&logoColor=black) ![Telegram](https://img.shields.io/badge/Telegram-26A5E4?style=flat&logo=telegram&logoColor=white) ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white) |

## 🔌 하드웨어 스펙 및 상세 사양 (Hardware Specifications)

| 구분 | 항목 | 상세 사양 |
| :--- | :--- | :--- |
| **Main Robot** | **AGV 모델** | **JetBot v0.4.0** 기반 커스텀 플랫폼 |
| **Controller** | **Main Biard** | **Raspberry Pi 5** (BCM2712 SoC) |
| **Edge AI** | **Accelerator** | **NVIDIA Jetson Nano** & Vision |
| **Vision** | **Camera** | 객체 인식 및 자율 주행용 Vision AI Camera |
| **Mechanics** | **Actuator** | 고성능 구동 모터 및 **환경 정리용 로봇팔** 탑재 |
| **Connectivity** | **Wireless** |  |

## 🌟 핵심 기능 (Key Features)

### 1. 자율 주행 & 객체 인식 (Robot)
- **Deep Learning Driving:** `ResNet-18` 모델을 학습시켜 곡선 및 교차로에서도 정밀한 라인 트레이싱 주행 구현.
- **AI Vision Safety:** `YOLOv5 (TFLite)` 모델을 활용하여 주행 경로 상의 사람, 장애물을 실시간 탐지하고 즉시 정지/회피.
- **Touch GUI:** `PyQt5` 기반의 터치스크린 UI를 탑재하여 현장에서 로봇 상태 확인 및 수동 조작 가능.

### 2. 실시간 관제 시스템 (Dashboard)
- **Digital Twin:** MQTT 통신을 통해 로봇의 물리적 위치(Pose)와 상태를 웹 맵에 0.1초 단위로 동기화.
- **Task Management:** 웹에서 목적지 설정 및 작업 명령(물품 배달, 수거 등)을 하달하고 진행 상황 모니터링.
- **Dashboard:** 배터리 전압, 적재 여부, 센서 데이터 및 에러 로그를 실시간 그래프로 시각화.

### 3. 초저지연 데이터 통신 & 파이프라인
- **MQTT Protocol:** 로봇(Edge)과 서버 간의 경량화된 메시징으로 제어 지연 시간 최소화.
- **Node-RED Flows:** 복잡한 제어 로직과 데이터 흐름(API, DB 저장, 알림)을 시각적으로 설계 및 관리.

## 🏗 시스템 아키텍처 (Architecture)

```mermaid
graph LR
    A[AGV Robot\n(PyQt + ResNet/YOLO)] <-->|MQTT| B(Node-RED\nServer);
    B <-->|WebSocket/HTTP| C[Web Dashboard\n(Vue.js)];
    B -->|Log Data| D[(Firebase DB)];
