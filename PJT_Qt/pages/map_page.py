import time
from PySide6.QtCore import Qt, QRectF, QPointF, QTimer, QPropertyAnimation, QEasingCurve, Property, QObject
from PySide6.QtGui import QColor, QPen, QBrush, QPainterPath, QPainter, QTransform
from PySide6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QGraphicsPathItem,
    QGraphicsEllipseItem
)
from config import CFG

class RippleItem(QObject, QGraphicsEllipseItem):
    def __init__(self, parent=None):
        QObject.__init__(self)
        # 시작 크기
        QGraphicsEllipseItem.__init__(self, -5, -5, 10, 10)

        # 선 두께를 3에서 5로 상향하여 더 진하게 보이게 함
        self.ripple_color = QColor(96, 165, 250) # 밝은 파란색
        self.setPen(QPen(self.ripple_color, 5))
        self.setBrush(Qt.NoBrush)
        self.setZValue(999)

        # 애니메이션 설정
        self.anim = QPropertyAnimation(self, b"rect_prop")
        self.anim.setDuration(1800) # 지속 시간을 1.2초에서 1.8초로 늘려 더 천천히 퍼지게 함
        self.anim.setStartValue(QRectF(-5, -5, 10, 10))

        # ★ 파동의 최대 크기를 140에서 250으로 대폭 상향!
        self.max_size = 250
        self.anim.setEndValue(QRectF(-self.max_size/2, -self.max_size/2, self.max_size, self.max_size))

        # 부드럽게 퍼지다가 멈추는 효과
        self.anim.setEasingCurve(QEasingCurve.OutExpo)

        self.anim.finished.connect(self.self_delete)
        self.anim.start()

    def get_rect_prop(self):
        return self.rect()

    def set_rect_prop(self, r):
        self.setRect(r)
        # 크기에 비례해서 투명도 조절 (사라지는 지점을 더 뒤로 늦춤)
        progress = r.width() / self.max_size
        alpha = max(0, int(255 * (1.0 - progress)))

        # 선 두께도 퍼질수록 살짝 얇아지게 하면 더 자연스러움
        pen_width = max(1, 5 * (1.0 - progress))
        self.setPen(QPen(QColor(96, 165, 250, alpha), pen_width))

    rect_prop = Property(QRectF, get_rect_prop, set_rect_prop)

    def self_delete(self):
        if self.scene():
            self.scene().removeItem(self)

# --- 2. 메인 맵 페이지 클래스 ---
class MapPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.px_per_m = 100.0

        # UI 파일 로드
        from page_ui.pages.ui_map import Ui_MapPage
        self.ui = Ui_MapPage()
        self.ui.setupUi(self)

        # 맵 영역 2:1 비율 고정
        if hasattr(self.ui, "horizontalLayout_root"):
            self.ui.horizontalLayout_root.setStretch(0, 2)
            self.ui.horizontalLayout_root.setStretch(1, 1)

        # 씬(Scene) 구성
        self.scene = QGraphicsScene(self)
        self.ui.mapView.setScene(self.scene)
        self.ui.mapView.setRenderHint(QPainter.Antialiasing)

        # 궤적 아이템 (Path)
        self.path_item = QGraphicsPathItem()
        self.path_item.setPen(QPen(QColor("#60a5fa"), 10, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.path_item.setZValue(99)
        self.scene.addItem(self.path_item)

        # 로봇 아이콘 (현재 위치)
        self.robot_item = QGraphicsEllipseItem(-15, -15, 30, 30)
        self.robot_item.setBrush(QBrush(QColor("#ffffff")))
        self.robot_item.setPen(QPen(Qt.black, 3))
        self.robot_item.setZValue(1001)
        self.scene.addItem(self.robot_item)

        self.trace_data = []

        # --- 왕왕이(Ripple) 발생 타이머 (1.5초 주기) ---
        self.ripple_timer = QTimer(self)
        self.ripple_timer.timeout.connect(self.create_ripple)
        self.ripple_timer.start(1500)

        # 버튼 및 슬라이더 이벤트 연결
        self.ui.btn_fit.clicked.connect(self.fit_view)
        self.ui.btn_clear_path.clicked.connect(self.clear_all)
        self.ui.sld_zoom.valueChanged.connect(self.update_zoom_from_slider)

        # 0.5초 뒤 초기 화면 맞춤 실행
        QTimer.singleShot(500, self.init_view)

    def create_ripple(self):
        """로봇의 실시간 위치에 파동 효과를 생성합니다."""
        if not self.trace_data: return

        last_pt = self.trace_data[-1]
        ripple = RippleItem()
        ripple.setPos(last_pt)
        self.scene.addItem(ripple)

    def meters_to_px(self, x, y):
        """좌표 스케일링 (/10) 적용"""
        scaled_x = float(x) / 10.0
        scaled_y = float(y) / 10.0
        return QPointF(scaled_x * self.px_per_m, scaled_y * self.px_per_m)

    def on_event_added(self, ev):
        """실시간 데이터 수신 및 궤적 그리기"""
        pose = ev.get("pose")
        if not pose: return

        pt = self.meters_to_px(pose.get("x", 0), pose.get("y", 0))
        self.trace_data.append(pt)

        # 궤적 패스 업데이트
        path = QPainterPath()
        if self.trace_data:
            path.moveTo(self.trace_data[0])
            for p in self.trace_data[1:]:
                path.lineTo(p)
        self.path_item.setPath(path)

        # 로봇 아이콘 이동
        self.robot_item.setPos(pt)
        self.ui.lbl_poses.setText(f"{len(self.trace_data)} pts")

        # 첫 데이터 수신 시 자동 Fit
        if len(self.trace_data) == 1:
            self.fit_view()

    def update_zoom_from_slider(self, value):
        """슬라이더에 따른 절대 배율 조절"""
        scale_factor = value / 100.0
        self.ui.mapView.setTransform(QTransform().scale(scale_factor, scale_factor))
        self.ui.lbl_zoom_value.setText(f"{value}%")

    def init_view(self):
        """초기 화면을 넓게 잡습니다."""
        base_rect = QRectF(-100, -100, 1200, 1200)
        self.ui.mapView.fitInView(base_rect, Qt.KeepAspectRatio)
        self.sync_slider()

    def fit_view(self):
        """궤적을 기준으로 화면에 꽉 차게 정렬 (넓은 여백 포함)"""
        rect = self.path_item.boundingRect()
        if rect.width() < 10:
            rect = QRectF(0, 0, 800, 800)

        # 여백을 넉넉하게 40% 주어서 시원하게 보이도록 설정
        padding = max(rect.width(), rect.height()) * 0.4
        target_rect = rect.adjusted(-padding, -padding, padding, padding)

        self.ui.mapView.fitInView(target_rect, Qt.KeepAspectRatio)
        self.sync_slider()

    def sync_slider(self):
        """fitInView 이후 변화된 배율을 슬라이더에 동기화"""
        current_scale = self.ui.mapView.transform().m11()
        zoom_percent = int(current_scale * 100)
        self.ui.sld_zoom.blockSignals(True)
        self.ui.sld_zoom.setValue(zoom_percent)
        self.ui.lbl_zoom_value.setText(f"{zoom_percent}%")
        self.ui.sld_zoom.blockSignals(False)

    def load_events(self, events, robot_id=None):
        self.clear_all()
        sorted_ev = sorted(events, key=lambda x: x.get("ts", 0))
        for ev in sorted_ev:
            if robot_id and str(ev.get("robot_id")) != str(robot_id): continue
            self.on_event_added(ev)

    def clear_all(self):
        self.trace_data = []
        self.path_item.setPath(QPainterPath())
        self.ui.lbl_poses.setText("0 pts")
