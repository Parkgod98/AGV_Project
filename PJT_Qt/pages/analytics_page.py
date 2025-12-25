import numpy as np
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel
import pyqtgraph as pg

from page_ui.pages.ui_analytics import Ui_AnalyticsForm
from utils.plot_theme import apply_plot_theme
from utils.themed_plot_widget import ThemedPlotWidget

class AnalyticsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_AnalyticsForm()
        self.ui.setupUi(self)

        # 1. KPI 레이아웃 생성 및 삽입
        kpi_row_layout = self._build_kpi_row()
        self.ui.hl_kpi_container.addLayout(kpi_row_layout)

        # 2. 그래프 객체 생성
        self.bar_plot = ThemedPlotWidget()
        self._style_plot(self.bar_plot, "Destination Ranking", "Location", "Visit Count")
        self.ui.vl_dest_container.addWidget(self.bar_plot)

        # 테마 적용 (QSS 로드 대기)
        QTimer.singleShot(100, lambda: apply_plot_theme(self.bar_plot))

    def update_analytics(self, tasks: list):
        if not tasks: return

        dest_counts = {}
        active_dates = set()
        done_count = 0

        for t in tasks:
            # (A) 활동 일수 집계
            c_at = t.get("created_at")
            if c_at:
                active_dates.add(str(c_at)[:10])

            # (B) 완료된 작업 및 장소 카운트
            if str(t.get("status", "")).lower() == "done":
                done_count += 1
                dest = str(t.get("target_area", "")).strip()
                if dest and dest.lower() != "charger":
                    dest_counts[dest] = dest_counts.get(dest, 0) + 1

        # 그래프 갱신
        self.update_bar_chart(dest_counts)

        # KPI 갱신 (존재하는 위젯만 업데이트)
        self.lb_kpi_total.setText(str(done_count))
        self.lb_kpi_active.setText(str(len(active_dates)))

        # ★ 위젯이 존재할 때만 텍스트 설정 (에러 방지)
        if hasattr(self, 'lb_kpi_dist'):
            self.lb_kpi_dist.setText("-")
        if hasattr(self, 'lb_kpi_avg_speed'):
            self.lb_kpi_avg_speed.setText("-")

    def update_bar_chart(self, data_dict):
        self.bar_plot.clear()
        if not data_dict: return

        sorted_data = dict(sorted(data_dict.items(), key=lambda item: item[1], reverse=True))
        labels = list(sorted_data.keys())
        values = list(sorted_data.values())
        x = np.arange(len(labels))

        bg = pg.BarGraphItem(
            x=x, height=values, width=0.6,
            brush=pg.mkBrush('#3b82f6'),
            pen=pg.mkPen('#60a5fa', width=1)
        )
        self.bar_plot.addItem(bg)

        ticks = [(i, label) for i, label in enumerate(labels)]
        self.bar_plot.getAxis('bottom').setTicks([ticks])

    def _make_kpi_card(self, title: str, value: str):
        card = QFrame()
        card.setObjectName("kpi_card")
        vl = QVBoxLayout(card)
        lb_title = QLabel(title); lb_title.setObjectName("kpi_title")
        lb_value = QLabel(value); lb_value.setObjectName("kpi_value")
        vl.addWidget(lb_title); vl.addWidget(lb_value)
        return card, lb_value

    def _build_kpi_row(self):
        """네 개의 카드를 모두 생성하여 MainWindow에서의 호출 에러를 방지합니다."""
        row = QHBoxLayout()
        # 4개의 카드를 모두 생성하여 변수에 할당
        c1, self.lb_kpi_total = self._make_kpi_card("Total Tasks", "0")
        c2, self.lb_kpi_active = self._make_kpi_card("Active Days", "0")

        for c in (c1, c2):
            row.addWidget(c, 1)
        return row

    def _style_plot(self, w: pg.PlotWidget, title: str, xlabel: str, ylabel: str):
        w.setBackground(None)
        w.setTitle(title, color='#3b82f6', size='11pt')
        w.setLabel("bottom", xlabel); w.setLabel("left", ylabel)
        w.showGrid(x=True, y=True, alpha=0.1)
