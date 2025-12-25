# mainwindow.py
import sys
import json
import time
from datetime import datetime

import pytz
import numpy as np
import cv2

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSplashScreen
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QFile, QTimer

from config import CFG
from page_ui.ui_form import Ui_MainWindow
from utils.mqtt_client import MqttClient
from utils.firestore_client import FirestoreConfig, FirestoreWorker
from utils.camera_worker import CameraWorker

from pages.overview_page import OverviewPage
from pages.control_page import ControlPage
from pages.analytics_page import AnalyticsPage
from pages.tasks_page import TasksPage
from pages.logs_page import LogsPage
from pages.map_page import MapPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tz = pytz.timezone("Asia/Seoul")

        # -------------------------
        # UI
        # -------------------------

        # UI setup
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # ---- Small-topbar for 800x480 (avoid overlap) ----
        try:
            self.ui.hl_nav.setSpacing(4)
            self.ui.frame_nav.setMinimumSize(0, 52)
            # shrink button minimum widths
            self.ui.btn_overview.setMinimumSize(90, 40)
            self.ui.btn_control.setMinimumSize(90, 40)
            self.ui.btn_analytics.setMinimumSize(100, 40)
            self.ui.btn_map.setMinimumSize(70, 40)
            self.ui.btn_tasks.setMinimumSize(70, 40)
            self.ui.btn_logs.setMinimumSize(70, 40)
            self.ui.lbl_top_status.setMinimumSize(150, 0)
        except Exception:
            pass

        # Pages
        self.page_overview = OverviewPage()
        self.page_control = ControlPage()
        self.page_analytics = AnalyticsPage()
        self.page_tasks = TasksPage()
        self.page_logs = LogsPage()

        # -------------------------
        # MapPage (호환 생성)
        # -------------------------
        # 1) 기존(v8 스타일) 생성자 인자 지원 시: 그대로
        # 2) 새 MapPage(인자 없는 스타일)일 경우: fallback + setter 방식 적용
        self.page_map = self._create_map_page_compatible()

        # Embed pages into placeholder pages from .ui
        self._embed(self.ui.page_overview, self.page_overview)
        self._embed(self.ui.page_control, self.page_control)
        self._embed(self.ui.page_analytics, self.page_analytics)
        self._embed(self.ui.page_tasks, self.page_tasks)
        self._embed(self.ui.page_logs, self.page_logs)
        self._embed(self.ui.page_map, self.page_map)

        # Nav Btn
        self.ui.btn_overview.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.btn_control.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.btn_analytics.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.btn_map.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(3))
        self.ui.btn_tasks.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(4))
        self.ui.btn_logs.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(5))

        # Theme
        self._try_load_qss(CFG.qss_dir)

        # -------------------------
        # MQTT (asynchronous)
        # -------------------------
        self.mqtt_ok = False
        self.mqtt = MqttClient(host=CFG.mqtt_host, port=CFG.mqtt_port, client_id="agv_hmi")
        self.mqtt.connected.connect(self.on_mqtt_connected)
        self.mqtt.disconnected.connect(self.on_mqtt_disconnected)
        self.mqtt.messageReceived.connect(self.on_mqtt_message)

        # mqtt_client.py에 log/error 시그널을 추가한 버전 기준
        if hasattr(self.mqtt, "log"):
            self.mqtt.log.connect(self.page_logs.append)
        if hasattr(self.mqtt, "error"):
            self.mqtt.error.connect(self.page_logs.append)

        # ✅ 중요: __init__에서 connect()로 막지 말고, 이벤트 루프 시작 직후에 시도
        QTimer.singleShot(0, self._start_mqtt)

        # -------------------------
        # Firestore (robots/tasks/events/interaction)
        # -------------------------
        self.fs_ok = False
        # Map events seeding guard (must be set before FS thread can emit)
        self._map_events_seeded = False
        self.fs = None
        if CFG.firestore_enabled:
            cfg = FirestoreConfig(
                service_account_path=CFG.service_account_path,
                robots_collection=CFG.fs_robots_collection,
                tasks_collection=CFG.fs_tasks_collection,
                events_collection=CFG.fs_events_collection,
                interaction_collection=CFG.fs_interaction_collection,
                events_pose_emit_interval_s=CFG.fs_events_pose_emit_interval_s,
            )
            self.fs = FirestoreWorker(cfg)
            self.fs.ready.connect(self.on_fs_ready)
            self.fs.log.connect(self.page_logs.append)
            self.fs.upload_ok.connect(lambda doc_id: self.page_logs.append(f"[FS] upload OK: {doc_id}"))
            self.fs.upload_fail.connect(lambda doc_id, e: self.page_logs.append(f"[FS] upload FAIL: {doc_id} ({e})"))

            # schema listeners
            self.fs.robots_updated.connect(self.on_robots_updated)
            self.fs.tasks_updated.connect(self.on_tasks_updated)
            self.fs.interactions_updated.connect(self.on_interactions_updated)
            self.fs.events_updated.connect(self.on_events_updated)
            # Optional per-event stream (better for maps/logs)
            if hasattr(self.fs, "event_added"):
                self.fs.event_added.connect(self.on_event_added)
            self.fs.start()

        # -------------------------
        # Camera (Jetson Nano Stream + PC YOLO Inference)
        # -------------------------
        self.cam_worker = None
        if CFG.camera_enabled:
            # 통합된 CameraWorker 인스턴스 생성
            self.cam_worker = CameraWorker(cfg=CFG)
            # 중요: CameraWorker의 frameReady 시그널을 MainWindow의 슬롯에 연결
            self.cam_worker.frameReady.connect(self.on_camera_frame)
            self.cam_worker.status.connect(self.page_logs.append)
            self.cam_worker.start()

        # Wire control signals
        self.page_control.interactionCommand.connect(self._handle_control_interaction)

        self._update_top_status()

        # demo: 배터리/센서 프로토 초기값
        self.page_overview.set_battery(0)
        self.page_overview.set_amount_of_task(0)
        self.page_overview.set_take_time(0)
        self.page_overview.set_temp(0)

    # -------------------------
    # MapPage compatibility layer
    # -------------------------
    def _create_map_page_compatible(self):
        """Create MapPage with backward/forward compatibility.

        - If MapPage supports world_w_m/world_h_m/px_per_m/enable_dummy in __init__, use it.
        - Otherwise, create MapPage() and configure using setter methods if present.
        """
        world_w = 10.0
        world_h = 10.0
        px_per_m = 80.0
        enable_dummy = getattr(CFG, "map_dummy_enabled", False)

        # 1) Try legacy signature
        try:
            page = MapPage(
                world_w_m=world_w,
                world_h_m=world_h,
                px_per_m=px_per_m,
                enable_dummy=enable_dummy,
            )
            # POI/Bounds가 별도로 필요하면 (메서드 있을 때만)
            self._map_apply_cfg_optional(page)
            return page
        except TypeError:
            pass

        # 2) Fallback: new signature
        page = MapPage()

        # optional config setters
        self._map_apply_cfg_optional(page, world_w, world_h, px_per_m)

        return page

    def _map_apply_cfg_optional(self, page, world_w=10.0, world_h=10.0, px_per_m=80.0):
        # world rect
        if hasattr(page, "set_world_rect"):
            try:
                page.set_world_rect(0.0, 0.0, float(world_w), float(world_h))
            except Exception:
                pass

        # pixel scale
        if hasattr(page, "set_px_per_m"):
            try:
                page.set_px_per_m(float(px_per_m))
            except Exception:
                pass

        # POIs
        if hasattr(CFG, "map_pois") and hasattr(page, "set_pois"):
            try:
                page.set_pois(CFG.map_pois)
            except Exception:
                pass

    # -------------------------
    # interaction logging (for HMI debug / audit)
    # -------------------------
    def _mk_interaction_id(self, kind: str) -> str:
        """Generate a unique interaction_id for writes from the Qt HMI."""
        stamp = datetime.now(self.tz).strftime("%Y%m%d_%H%M%S_%f")
        hmi_uid = getattr(CFG, "hmi_user_id", "rpi_hmi_01")
        return f"it_{stamp}_{hmi_uid}_{kind}_{CFG.robot_id}"

    def _log_interaction(self, input_mode: str, raw_input, result: str = "sent", error: str | None = None):
        """Write an interaction document (best-effort)."""
        if not getattr(CFG, "hmi_log_interaction", True):
            return
        if not getattr(CFG, "firestore_enabled", False):
            return
        if self.fs is None:
            return

        ts_ms = int(time.time() * 1000)
        doc_id = self._mk_interaction_id(input_mode)

        data = {
            "interaction_id": doc_id,
            "input_mode": input_mode,
            "raw_input": raw_input,
            "parsed": None,
            "result": result,
            "error": error,
            "source": getattr(CFG, "hmi_source", "hmi_qt"),
            "user_id": getattr(CFG, "hmi_user_id", "rpi_hmi_01"),
            "robot_id": str(CFG.robot_id),
            "ts": ts_ms,
        }

        col = getattr(CFG, "fs_interaction_collection", "interaction")
        self.fs.request_upload(col, doc_id, data)

    # -------------------------
    # internal helpers
    # -------------------------
    def _start_mqtt(self):
        try:
            self.page_logs.append("[BOOT] MQTT start (non-blocking)")
            self.mqtt.connect_to_host()
        except Exception as e:
            self.page_logs.append(f"[BOOT] MQTT start failed: {e}")
            self.mqtt_ok = False
            self._update_top_status()

    def _embed(self, container: QWidget, w: QWidget):
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(w)

    def _try_load_qss(self, path: str):
        f = QFile(path)
        if f.exists() and f.open(QFile.ReadOnly):
            self.setStyleSheet(str(f.readAll(), "utf-8"))
            f.close()

    # ---------- Status UI ----------
    def _update_top_status(self):
        status_text = f"MQTT: {'OK' if self.mqtt_ok else 'NO'} | FS: {'OK' if self.fs_ok else 'NO'}"
        self.ui.lbl_top_status.setText(status_text)
        self.page_overview.set_connection_summary(CFG.robot_id)

    # ---------- MQTT ----------
    def on_mqtt_connected(self):
        self.mqtt_ok = True
        self.page_logs.append("[MQTT] Connected")

        self.mqtt.subscribe(f"/robot/{CFG.robot_id}/status/#")
        self.mqtt.subscribe("cmd/+/request")
        self.mqtt.subscribe("telemetry/#")

        self._update_top_status()

    def on_mqtt_disconnected(self):
        self.mqtt_ok = False
        self.page_logs.append("[MQTT] Disconnected")
        self._update_top_status()

    def on_mqtt_message(self, topic: str, payload: str):
        # 젯슨 나노가 보내는 추론 결과 토픽 (예: /robot/agv1/inference/yolo)
        if topic == f"/robot/{CFG.robot_id}/inference/yolo":
            try:
                # 젯슨에서 보낸 JSON 데이터를 파이썬 리스트/딕셔너리로 변환
                self.current_inference = json.loads(payload)
            except Exception as e:
                self.page_logs.append(f"[JSON Error] Inference parse fail: {e}")

        if topic.startswith("cmd/") or topic.startswith(f"/robot/{CFG.robot_id}/status/"):
            self.page_logs.append(f"[MQTT] {topic} -> {payload}")

        base = f"/robot/{CFG.robot_id}/status/"
        if topic.startswith(base):
            key = topic[len(base):]
            self._handle_status(key, payload)
            return

        if topic.endswith("/request") and topic.startswith("cmd/"):
            try:
                data = json.loads(payload)
            except Exception:
                data = {"raw": payload}
            self.page_logs.append(f"[REQ-MON] {topic} -> {data}")
            return

        if topic == f"/robot/{CFG.robot_id}/inference/yolo":
            try:
                self.current_inference = json.loads(payload) # [{"box": [x,y,w,h], "cls": 0, "conf": 0.8}, ...]
            except: pass

    def _handle_control_interaction(self, input_mode: str, raw_data: any, parsed_data: dict):
        """
        ControlPage의 모든 조작(이동, 그랩, 서보 등)을 처리합니다.
        사용자 정의 포맷에 따라 robot_id는 제외하고 저장합니다.
        """
        # 1. MQTT 토픽 및 페이로드 설정
        # parsed_data에 이미 mqtt_topic과 mqtt_payload가 포함되어 있다고 가정합니다.
        topic = parsed_data.get("mqtt_topic", f"/robot/{CFG.robot_id}/cmd")
        payload = parsed_data.get("mqtt_payload", parsed_data)

        # 2. MQTT 전송
        if self.mqtt_ok:
            self.mqtt.publish(topic, payload)
            result = "sent"
            error_msg = None
        else:
            result = "fail"
            error_msg = "MQTT_DISCONNECTED"

        # 3. Firestore 저장용 JSON 구성 (사용자 요청 포맷 반영)
        ts_ms = int(time.time() * 1000)
        doc_id = self._mk_interaction_id(input_mode)

        db_json = {
            "interaction_id": doc_id,
            "input_mode": input_mode,
            "source": getattr(CFG, "hmi_source", "hmi_qt"),
            "user_id": getattr(CFG, "hmi_user_id", "rpi_hmi_01"),
            "raw_input": str(raw_data),
            "parsed": parsed_data,
            "result": result,
            "error": error_msg,
            "ts": ts_ms, # 정렬을 위해 ts는 유지하는 것을 권장합니다
            "linked_at": ts_ms # 별도의 연결 Task가 없다면 현재 시각으로 설정
        }

        # 4. Firestore 업로드 요청
        if self.fs and CFG.firestore_enabled:
            self.fs.request_upload(CFG.fs_interaction_collection, doc_id, db_json)
            self.page_logs.append(f"[CONTROL] {input_mode} {result}")

    def _handle_status(self, key: str, payload: str):
        try:
            if key == "battery":
                self.page_overview.set_battery(int(float(payload)))
            elif key == "temp":
                self.page_overview.set_temp(float(payload))
            elif key == "amount_of_task":
                self.page_overview.set_amount_of_task(int(float(payload)))
            elif key == "take_time":
                self.page_overview.set_take_time(int(float(payload)))
            elif key == "pose":
                if not getattr(CFG, "map_use_mqtt_pose", False):
                    return

                try:
                    obj = json.loads(payload)
                    x = float(obj.get("x", 0.0))
                    y = float(obj.get("y", 0.0))
                    yaw = float(obj.get("yaw", 0.0))
                    yaw_unit = str(obj.get("yaw_unit", "rad")).lower()

                    if yaw_unit in ("deg", "degree", "degrees"):
                        yaw = float(np.deg2rad(yaw))

                    t = obj.get("t", None)
                    if t is not None:
                        t = float(t)
                        if t > 1e11:
                            t = t / 1000.0
                    else:
                        t = None

                    # ✅ MapPage API 호환: append_pose / push_pose 둘 다 지원
                    if hasattr(self.page_map, "append_pose"):
                        self.page_map.append_pose(x, y, yaw, t=t)
                    elif hasattr(self.page_map, "push_pose"):
                        self.page_map.push_pose(x, y, yaw=yaw, ts=t)
                    else:
                        # 최소한 안 죽게
                        pass
                except Exception as e:
                    self.page_logs.append(f"[POSE] parse fail: {e} payload={payload}")
                return

            elif key == "route":
                try:
                    obj = json.loads(payload)
                    xy = obj.get("xy", [])
                    events = obj.get("events", [])
                    self.page_analytics.update_route(xy, events)
                except Exception as e:
                    self.page_logs.append(f"[ROUTE] parse fail: {e}")
                return
            elif key == "timeseries":
                obj = json.loads(payload)
                y = obj.get("y", [])
                self.page_analytics.update_timeseries(y)
        except Exception as e:
            self.page_logs.append(f"[MQTT Parse Error] {key}: {e}")

    def publish_task_from_ui(self, topic: str, payload: dict):
        if self.mqtt_ok:
            self.mqtt.publish(topic, payload)
            result = "sent"
            err = None
        else:
            result = "mqtt_disconnected"
            err = "MQTT not connected"
            self.page_logs.append("[WARN] MQTT not connected: task publish skipped")

        self.page_logs.append(f"[TASK PUB] {topic} {payload} ({result})")

        self._log_interaction(
            input_mode="task_request",
            raw_input={
                "topic": topic,
                "payload": payload,
            },
            result=result,
            error=err,
        )

    # ---------- Firestore ----------

    def on_fs_ready(self, ok: bool):
        self.fs_ok = bool(ok)
        self._update_top_status()

    def on_tasks_updated(self, tasks: list):
        """DB에서 tasks 컬렉션이 업데이트될 때 호출됨"""
        if not tasks:
                return

        # 1. Task 리스트 페이지 갱신
        self.page_tasks.set_tasks(tasks)

        # 2. Overview 통계 계산
        # 상태가 'done'인 것만 필터링하거나 전체 이력을 대상으로 함
        completed_tasks = [t for t in tasks if t.get("status") == "done"]

        # (1) 수행한 task 개수
        total_count = len(completed_tasks)
        self.page_overview.set_amount_of_task(total_count)

        # (2) 누적 수행 시간 계산 (ms 단위 합산 -> sec 단위 변환)
        # 만약 '평균'이 아닌 '총 가동 시간'을 원하신다면 sum을 사용
        total_time_ms = sum(t.get("actual_duration_ms", 0) for t in completed_tasks)
        total_time_sec = total_time_ms / 1000.0

        self.page_overview.set_take_time(int(total_time_sec))

        if hasattr(self, 'page_analytics'):
                self.page_analytics.update_analytics(tasks)

    def on_interactions_updated(self, interactions: list):
        self.page_tasks.set_interactions(interactions)

    # -------------------------
    # Firestore Events & Map Update
    # -------------------------
    def on_events_updated(self, events: list):
        """과거 전체 이벤트 로드 시"""
        if not events:
            return
        # map_page.py에 추가한 load_events 함수 호출
        # AttributeError 방지를 위해 hasattr 체크 추가 (안전 장치)
        if hasattr(self.page_map, "load_events"):
            self.page_map.load_events(events, robot_id=CFG.robot_id)

    def on_event_added(self, ev: dict):
        """실시간 새 이벤트 추가 시"""
        try:
            if not isinstance(ev, dict):
                return
            if str(ev.get("robot_id", "")) != str(CFG.robot_id):
                return

            # 실시간 궤적을 위해 map_page.py의 on_event_added 호출
            if hasattr(self.page_map, "on_event_added"):
                self.page_map.on_event_added(ev)
        except Exception as e:
            self.page_logs.append(f"[MAP-ERR] Real-time update fail: {e}")

    def on_db_update(self):
        # Firestore에서 받아온 최신 tasks와 events 리스트
        tasks = self.fs.get_collection("tasks")
        events = self.fs.get_collection("events")

        # Analytics 페이지로 전달
        self.page_analytics.update_analytics(tasks, events)

    def on_robots_updated(self, robots: list):
        try:
            cur = None
            for r in robots:
                if str(r.get("robot_id", "")) == str(CFG.robot_id):
                    cur = r
                    break
            if cur is None and robots:
                cur = robots[0]

            if not cur:
                return

            batt = cur.get("battery", None)
            temp = cur.get("cpu_temp", None)
            if batt is not None:
                try:
                    self.page_overview.set_battery(int(float(batt)))
                except Exception:
                    pass
            if temp is not None:
                try:
                    self.page_overview.set_temp(int(float(temp)))
                except Exception:
                    pass

            pose = cur.get("pose", None)
            if isinstance(pose, dict):
                x = pose.get("x", None)
                y = pose.get("y", None)
                theta = pose.get("theta", None)
                if x is not None and y is not None and theta is not None:
                    try:
                        if hasattr(self.page_map, "update_current_pose"):
                            self.page_map.update_current_pose(float(x), float(y), float(theta))
                        elif hasattr(self.page_map, "push_pose"):
                            self.page_map.push_pose(float(x), float(y), yaw=float(theta), ts=None)
                    except Exception:
                        pass
        except Exception:
            pass

        # -------------------------
        # Camera Frame Handling
        # -------------------------
        def on_camera_frame(self, pixmap):
            """
            통합형 CameraWorker가 추론(YOLO)까지 마친 QPixmap을 보내줍니다.
            이를 그대로 ControlPage에 표시합니다.
            """
            if pixmap and not pixmap.isNull():
                # 이미 추론 결과(박스)가 그려진 상태이므로 바로 UI에 업데이트
                self.page_control.set_camera_pixmap(pixmap)

    def closeEvent(self, event):
        try:
            if self.cam is not None:
                self.cam.stop()
                self.cam.quit()
                self.cam.wait()
        except Exception:
            pass

        try:
            if self.fs is not None:
                self.fs.stop()
                self.fs.quit()
                self.fs.wait()
        except Exception:
            pass

        try:
            self.mqtt.disconnect_from_host()
        except Exception:
            pass

        event.accept()

    def on_camera_frame(self, pixmap):
            """
            CameraWorker(PC 직접 추론 버전)가 YOLO 분석을 마친 프레임을 보내주면
            ControlPage의 카메라 뷰에 출력합니다.
            """
            if pixmap and not pixmap.isNull():
                # 이미 박스가 그려진 QPixmap이 넘어오므로 그대로 표시만 하면 됩니다.
                self.page_control.set_camera_pixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 1. 로딩 이미지 로드 및 설정
    pixmap = QPixmap("assets/loading_bg.png")
    splash = QSplashScreen(pixmap)

    # 텍스트 스타일 설정 (theme.qss와 일치시킴)
    splash.show()

    # 2. 메인 윈도우 인스턴스 생성 (이때 MQTT/FS 초기화가 시작됨)
    win = MainWindow()

    # 3. 일정 시간 후 또는 데이터 준비 시 메인 윈도우 표시
    # '뚱딱' 거리는 느낌을 없애기 위해 약 1.5~2초 정도 여유를 줍니다.
    def start_main():
        win.show()
        splash.finish(win)

    # 2초 뒤에 메인 화면으로 전환
    QTimer.singleShot(2000, start_main)

    sys.exit(app.exec())
