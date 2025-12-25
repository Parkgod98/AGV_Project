import time
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal
from page_ui.pages.ui_control import Ui_ControlForm

class ControlPage(QWidget):
    # MainWindow와의 통신을 위한 시그널
    interactionCommand = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ControlForm()
        self.ui.setupUi(self)

        self.is_connected = False

        # 카메라 영역과 제어 영역 비율 설정 (2:1)
        self.ui.horizontalLayout_root.setStretch(0, 1)
        self.ui.horizontalLayout_root.setStretch(1, 2)

        self.init_style()
        self.bind_events()

    def init_style(self):
        self.setStyleSheet("""
            QGroupBox { font-size: 13px; font-weight: bold; color: white; border: 1px solid #333a45; margin-top: 10px; padding-top: 15px; }
            QLabel { font-size: 11px; color: #ced4da; }
            QPushButton#btn_connect { background-color: #2d5af1; font-size: 14px; font-weight: bold; color: white; border-radius: 5px; }
            QPushButton { background-color: #2a2f3b; color: white; border-radius: 4px; padding: 5px; }
            QSlider::handle:horizontal { background: #60a5fa; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; }
        """)

    def bind_events(self):
        self.ui.btn_connect.clicked.connect(self.toggle_connection)

        # 이동 버튼 (Pressed/Released 기반)
        for btn, direction in [
            (self.ui.btn_up, "forward"), (self.ui.btn_down, "backward"),
            (self.ui.btn_left, "left"), (self.ui.btn_right, "right")
        ]:
            btn.pressed.connect(lambda d=direction: self.send_cmd("move", d))
            btn.released.connect(lambda: self.send_cmd("move", "stop"))

        self.ui.btn_stop.clicked.connect(lambda: self.send_cmd("move", "stop"))

        # 스피드 및 그랩
        self.ui.sld_speed.valueChanged.connect(lambda v: self.send_cmd("speed", v))
        self.ui.dial_grab.valueChanged.connect(self._on_grab_changed)

        # 서보 슬라이더 5개 (번호별 매핑)
        self.ui.sld_s1.valueChanged.connect(lambda v: self._on_servo_changed(1, v))
        self.ui.sld_s2.valueChanged.connect(lambda v: self._on_servo_changed(2, v))
        self.ui.sld_s3.valueChanged.connect(lambda v: self._on_servo_changed(3, v))
        self.ui.sld_s4.valueChanged.connect(lambda v: self._on_servo_changed(4, v))
        self.ui.sld_s5.valueChanged.connect(lambda v: self._on_servo_changed(5, v))

    def _on_grab_changed(self, v):
        self.ui.lbl_grab_title.setText(f"Grab: {v}%")
        self.send_cmd("grab", v)

    def _on_servo_changed(self, num, val):
        label = getattr(self.ui, f"lbl_s{num}")
        label.setText(f"S{num}: {val}°")
        self.send_cmd("arm", {"servo": num, "angle": val})

    def toggle_connection(self):
        if not self.is_connected:
            self.is_connected = True
            self.ui.btn_connect.setText("CONNECTED (READY)")
            self.ui.btn_connect.setStyleSheet("background-color: #10b981; color: white; font-weight: bold;")
        else:
            self.is_connected = False
            self.ui.btn_connect.setText("CONNECT TO AGV")
            self.ui.btn_connect.setStyleSheet("background-color: #2d5af1; color: white;")

    def send_cmd(self, action, value):
        if not self.is_connected: return
        cmd = {"action": action, "value": value, "ts": time.time()}
        self.interactionCommand.emit(cmd)

    def update_camera_frame(self, pixmap):
        """MainWindow에서 호출하여 카메라 화면 갱신"""
        self.ui.lbl_camera_view.setPixmap(pixmap)
