import time
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal
# 파일 위치가 꼬였을 수 있으니 명확히 임포트
try:
    from page_ui.pages.ui_control import Ui_ControlForm
except ImportError:
    from page_ui.ui_control import Ui_ControlForm

class ControlPage(QWidget):
    # MainWindow와 일치시킨 시그널: (mode, raw, parsed)
    interactionCommand = Signal(str, object, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ControlForm()
        self.ui.setupUi(self)

        self.is_connected = False

        # UI 비율 강제 조정 (제어판 1 : 카메라 2)
        self.ui.horizontalLayout_root.setStretch(0, 1)
        self.ui.horizontalLayout_root.setStretch(1, 2)

        self.init_style()
        self.bind_events()

    def init_style(self):
        # 카메라 뷰 대기 화면 및 테두리 테마 적용
        self.ui.frameCamera.setStyleSheet("""
            background-color: #000000;
            border: 2px solid #333a45;
            border-radius: 20px;
        """)
        self.ui.lbl_camera_view.setText("WAITING FOR AGV CAMERA...")
        self.ui.lbl_camera_view.setStyleSheet("color: #777; font-weight: bold; border: none;")

        # 버튼 및 그룹박스 스타일
        self.setStyleSheet("""
            QGroupBox { font-size: 15px; font-weight: bold; color: white; border: 1px solid #444; margin-top: 5px; padding-top: 15px; }
            QLabel { font-size: 13px; color: #ddd; }
            QPushButton#btn_connect { background-color: #2d5af1; font-size: 18px; font-weight: bold; color: white; border-radius: 10px; }
            QPushButton { background-color: #2a2f3b; color: white; border-radius: 8px; font-size: 16px; }
            QSlider::handle:horizontal { background: #60a5fa; width: 22px; height: 22px; margin: -8px 0; border-radius: 11px; }
        """)

    def bind_events(self):
        self.ui.btn_connect.clicked.connect(self.toggle_connection)

        # 🚀 수동 이동 버튼 이벤트 (Pressed=전송, Released=정지)
        # 람다 함수를 사용하여 인자를 정확히 전달
        self.ui.btn_up.pressed.connect(lambda: self.emit_mqtt("move", "forward"))
        self.ui.btn_down.pressed.connect(lambda: self.emit_mqtt("move", "backward"))
        self.ui.btn_left.pressed.connect(lambda: self.emit_mqtt("move", "left"))
        self.ui.btn_right.pressed.connect(lambda: self.emit_mqtt("move", "right"))

        # 버튼에서 손을 떼면 STOP
        stop_btns = [self.ui.btn_up, self.ui.btn_down, self.ui.btn_left, self.ui.btn_right]
        for b in stop_btns:
            b.released.connect(lambda: self.emit_mqtt("move", "stop"))

        self.ui.btn_stop.clicked.connect(lambda: self.emit_mqtt("move", "stop"))

        # 속도 및 그랩
        self.ui.sld_speed.valueChanged.connect(lambda v: self.emit_mqtt("speed", v))
        self.ui.dial_grab.valueChanged.connect(self._on_grab_changed)

        # 서보 1, 2, 3 (4, 5는 UI에서 삭제될 예정이므로 3까지만 연결)
        for i in range(1, 4):
            if hasattr(self.ui, f"sld_s{i}"):
                sld = getattr(self.ui, f"sld_s{i}")
                sld.valueChanged.connect(lambda v, n=i: self._on_servo_changed(n, v))

    def _on_grab_changed(self, v):
        self.ui.lbl_grab_title.setText(f"Grab (S4): {v}°")
        self.emit_mqtt("arm", {"servo": 4, "angle": v})

    def _on_servo_changed(self, n, v):
        lbl = getattr(self.ui, f"lbl_s{n}")
        lbl.setText(f"S{n}: {v}°")
        self.emit_mqtt("arm", {"servo": n, "angle": v})

    def toggle_connection(self):
        self.is_connected = not self.is_connected
        if self.is_connected:
            self.ui.btn_connect.setText("AGV CONNECTED")
            self.ui.btn_connect.setStyleSheet("background-color: #10b981; color: white; font-weight: bold;")
            self.emit_mqtt("system", "connect")
        else:
            self.ui.btn_connect.setText("CONNECT TO AGV")
            self.ui.btn_connect.setStyleSheet("background-color: #2d5af1; color: white;")
            self.emit_mqtt("system", "disconnect")

    def emit_mqtt(self, action, value):
        # 연결 안 됐을 때 system 명령 외에는 무시
        if not self.is_connected and action != "system":
            return

        # 🚀 MainWindow.py가 원하는 3단 구조 (input_mode, raw_data, parsed_data)
        parsed_data = {
            "mqtt_topic": "interaction/parsed",
            "mqtt_payload": {
                "action": action,
                "value": value,
                "ts": int(time.time() * 1000)
            }
        }
        self.interactionCommand.emit(action, str(value), parsed_data)

    def set_camera_pixmap(self, pixmap):
        if pixmap and not pixmap.isNull():
            self.ui.lbl_camera_view.setPixmap(pixmap.scaled(
                self.ui.lbl_camera_view.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
