from PySide6.QtWidgets import QWidget
from page_ui.pages.ui_overview import Ui_OverviewForm

class OverviewPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_OverviewForm()
        self.ui.setupUi(self)

        # UI Stretch 설정 (uic 변환 시 누락 대비)
        try:
            g = self.ui.grid_cards_2x2
            g.setRowStretch(0, 1)
            g.setRowStretch(1, 1)
            g.setColumnStretch(0, 1)
            g.setColumnStretch(1, 1)
        except Exception:
            pass

    def set_connection_summary(self, robot_id: str):
        """상단 상태바 정보 업데이트"""
        self.ui.lbl_robot_id.setText(f"ROBOT: {robot_id}")

    def set_battery(self, pct: int):
        """배터리 잔량 업데이트 (0~100)"""
        self.ui.lbl_batt_value.setText(str(max(0, min(100, int(pct)))))

    def set_temp(self, v: float):
        """CPU 온도 업데이트 (소수점 1자리)"""
        self.ui.lbl_temp_value.setText(f"{float(v):.1f}")

    def set_amount_of_task(self, v: int):
        """총 수행 task 개수 업데이트"""
        self.ui.lbl_task_value.setText(str(int(v)))

    def set_take_time(self, seconds: int):
            """초 단위를 받아서 일, 시, 분, 초 단위로 변환하여 출력"""
            seconds = int(seconds)

            if seconds < 60:
                # 60초 미만: 초 단위
                display_text = str(seconds)
                unit_text = "sec"
            elif seconds < 3600:
                # 1시간 미만: 분 단위 (예: 5.2 min)
                display_text = f"{seconds / 60:.1f}"
                unit_text = "min"
            elif seconds < 86400:
                # 24시간 미만: 시간 단위 (예: 3.5 hr)
                display_text = f"{seconds / 3600:.1f}"
                unit_text = "hr"
            else:
                # 24시간 이상: 일 단위 (예: 1.2 day)
                display_text = f"{seconds / 86400:.1f}"
                unit_text = "day"

            # 값(Value) 업데이트
            self.ui.lbl_time_value.setText(display_text)
            # 하단 단위(Unit) 라벨도 동적으로 변경
            self.ui.lbl_time_unit.setText(unit_text)
