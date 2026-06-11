import time
import os
import sys
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QPixmap

# 1. 파일 경로 인식을 위한 설정 (ModuleNotFoundError 방지)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 2. 업로드해주신 CameraWorker와 UI 불러오기
from utils.camera_worker import CameraWorker
from page_ui.pages.ui_control import Ui_ControlForm

class ControlPage(QWidget):
    # MainWindow로 제어 명령을 전달하기 위한 시그널
    interactionCommand = Signal(str, object, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ControlForm()
        self.ui.setupUi(self)
        self.is_connected = False

        # 3. YOLO 및 카메라 설정 (cfg 객체 구성)
        class Config:
            yolo_model_path = "models/best_fp16.tflite" # 실제 모델 경로 확인
            yolo_conf_thres = 0.5
            yolo_iou_thres = 0.45
            # 젯슨 나노의 IP 주소 (MQTT용)
            agv_ip = "10.236.94.250"
            robot_id = "agv1"

        self.cfg = Config()

        # 4. 통합 카메라 & 추론 워커 실행
        self.worker = CameraWorker(self.cfg)
        self.worker.frameReady.connect(self.update_camera_view)
        self.worker.status.connect(lambda msg: print(f"[CAMERA/YOLO] {msg}"))
        self.worker.start()

        self.init_layout_optimization()
        self.bind_events()

    @Slot(QPixmap)
    def update_camera_view(self, pixmap):
        # CameraWorker에서 보낸 (YOLO 박스가 그려진) 영상을 화면에 출력
        if not pixmap.isNull():
            self.ui.lbl_camera_view.setPixmap(pixmap.scaled(
                self.ui.lbl_camera_view.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))

    def init_layout_optimization(self):
        # [이전 요청 반영] 라즈베리 파이 800x480 최적화 레이아웃
        self.ui.horizontalLayout_root.setContentsMargins(1, 1, 1, 1)
        self.ui.horizontalLayout_root.setSpacing(2)
        self.ui.verticalLayout_left.setSpacing(0)

        # 버튼 높이 줄이기 (터치 가능한 최소 높이 24px)
        for btn in [self.ui.btn_up, self.ui.btn_down, self.ui.btn_left, self.ui.btn_right, self.ui.btn_stop]:
            btn.setFixedSize(42, 24)

        # Speed/Grab 간격 밀착을 위한 스타일 시트
        self.setStyleSheet("""
            QGroupBox { font-size: 10px; font-weight: bold; color: white; border: 1px solid #444; margin-top: 2px; }
            QLabel { font-size: 9px; color: #bbb; margin-bottom: -5px; }
            QPushButton { font-size: 10px; background-color: #2a2f3b; color: white; border-radius: 3px; }
            #frameCamera { background-color: #000; border-radius: 8px; }
        """)

    def bind_events(self):
        self.ui.btn_connect.clicked.connect(self.toggle_connection)

        # 수동 조작 (Pressed 시 이동, Released 시 정지)
        move_map = {
            self.ui.btn_up: "forward",
            self.ui.btn_down: "backward",
            self.ui.btn_left: "left",
            self.ui.btn_right: "right"
        }
        for btn, direction in move_map.items():
            btn.pressed.connect(lambda d=direction: self.emit_control_signal("move", d))
            btn.released.connect(lambda: self.emit_control_signal("move", "stop"))

        self.ui.btn_stop.clicked.connect(lambda: self.emit_control_signal("move", "stop"))

        # 속도 및 서보 슬라이더 이벤트
        self.ui.sld_speed.valueChanged.connect(self._on_speed_changed)
        self.ui.dial_grab.valueChanged.connect(self._on_grab_changed)
        for i in range(1, 4):
            getattr(self.ui, f"sld_s{i}").valueChanged.connect(
                lambda v, n=i: self._on_servo_changed(n, v))

    def _on_speed_changed(self, v):
        self.ui.lbl_speed_text.setText(f"Speed: {v}%")
        self.emit_control_signal("speed", v)

    def _on_grab_changed(self, v):
        self.ui.lbl_grab_text.setText(f"Grab: {v}%")
        self.emit_control_signal("arm", {"servo": 4, "angle": v})

    def _on_servo_changed(self, n, v):
        getattr(self.ui, f"lbl_s{n}").setText(f"S{n}: {v}°")
        self.emit_control_signal("arm", {"servo": n, "angle": v})

    def toggle_connection(self):
        self.is_connected = not self.is_connected
        text = "CONNECTED" if self.is_connected else "CONNECT TO AGV"
        color = "#10b981" if self.is_connected else "#2d5af1"
        self.ui.btn_connect.setText(text)
        self.ui.btn_connect.setStyleSheet(f"background-color: {color}; color: white;")

    def emit_control_signal(self, action, value):
        if not self.is_connected: return

        # AGV 수신 코드와 규격을 맞춘 MQTT 페이로드 생성
        parsed_data = {
            "mqtt_topic": f"/robot/{self.cfg.robot_id}/cmd",
            "mqtt_payload": {
                "mode": action,
                "direction": value if isinstance(value, str) else None,
                "value": value,
                "speed": self.ui.sld_speed.value() / 100.0,
                "ts": int(time.time() * 1000)
            }
        }
        # MainWindow를 통해 MQTT 메시지 전송
        self.interactionCommand.emit(action, str(value), parsed_data)

    def closeEvent(self, event):
        self.worker.running = False
        self.worker.wait()
        event.accept()
