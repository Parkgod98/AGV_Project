# config.py
from dataclasses import dataclass, field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

@dataclass
class AppConfig:
    robot_id: str = "agv1"

    # =====================
    # Theme
    # =====================
    qss_dir: str = "assets/qss/theme.qss"

    # =====================
    # MQTT
    # =====================
    mqtt_host: str = "10.41.145.221"
    mqtt_port: int = 1883

    # =====================
    # Firestore
    # =====================
    firestore_enabled: bool = True
    service_account_path: str = "assets/secrets/ssafy_embedded_qt-gui-controller.json"

    # Firestore schema collections
    fs_robots_collection: str = "robots"
    fs_tasks_collection: str = "tasks"
    fs_events_collection: str = "events"
    fs_interaction_collection: str = "interactions"

    # Firestore events can be noisy if pose updates are logged frequently.
    # This controls the *minimum* interval for streaming pose-like events to the UI.
    # - 1.0  : emit at most once per second per robot
    # - 0.0  : disable throttling
    fs_events_pose_emit_interval_s: float = 1.0

    # =====================
    # HMI identity (for interaction logging)
    # =====================
    hmi_source: str = "hmi_qt"      # interaction.source
    hmi_user_id: str = "rpi_hmi_01" # interaction.user_id (라파 Qt 주체)
    hmi_log_interaction: bool = True

    # =====================
    # Map / Pose source
    # =====================
    # # If True, MapPage will ingest pose updates from MQTT (/status/pose).
    # # Recommended False when Firestore schema (robots/events) is the source of truth.
    # map_use_mqtt_pose: bool = False

    # # If True, MapPage generates a dummy wandering trajectory for UI testing.
    # # Keep this False for real robot operation.
    # map_dummy_enabled: bool = False

    # # Preset POIs for MapPage (name, x_m, y_m)
    # # Customize as needed for your facility/map
    # map_pois: list[tuple[str, float, float]] = field(default_factory=lambda: [
    #     ("Home", 5.0, 5.0),
    #     ("Dock", 1.0, 1.0),
    #     ("RoomA", 8.0, 2.0),
    # ])

    # =========================
    # MAP (ADD THESE)
    # =========================

    # "실제 사용 맵"을 참고한 POI 고정 배치 (미터 좌표)
    # 좌표계: (0,0) = 좌상단, x는 오른쪽, y는 아래로 증가 (기본)
    # 만약 위아래 뒤집혀 보이면 map_flip_y=True로 바꾸면 됨.
    map_flip_y = False

    # 장소 블록 + 라벨 표시
    map_show_poi_labels = True
    map_poi_box_px = 22        # POI 컬러 사각형 크기(px)
    map_poi_label_dx = 12      # 라벨 x 오프셋
    map_poi_label_dy = -14     # 라벨 y 오프셋

    # 경로 그릴지(원하면 False 가능)
    map_path_enabled = True
    map_path_color = "#60a5fa"
    map_path_width = 2

    # 로봇 표시 + 파동 효과
    map_robot_color = "#e7eaf0"
    map_pulse_color = "#60a5fa"
    # 1. 맵 월드 크기를 좌표 최대값(100)보다 크게 설정
    map_world_w_m = 110.0  # 10.0 -> 110.0으로 수정
    map_world_h_m = 110.0  # 10.0 -> 110.0으로 수정

    # 2. 미터당 픽셀(px_per_m)을 줄여야 지도가 모니터 밖으로 안 나감
    # (전체 지도가 1000px 정도 되도록 10.0 정도로 조절)
    px_per_m = 10.0        # 80.0 -> 10.0으로 수정

    # 3. POI 위치 정보 업데이트 (받으신 데이터 반영)
    map_pois_m = [
        {"name": "Charger", "x": 5.0, "y": 1.0, "color": "#f59e0b"}, # 50/10, 10/10
        {"name": "Water",   "x": 1.8, "y": 2.8, "color": "#22c55e"}, # 18/10, 28/10
        {"name": "Basket",  "x": 8.2, "y": 4.2, "color": "#eab308"}, # 82/10, 42/10
        {"name": "Room_A",  "x": 2.0, "y": 7.0, "color": "#a855f7"}, # 20/10, 70/10
        {"name": "Room_B",  "x": 4.2, "y": 8.2, "color": "#3b82f6"}, # 42/10, 82/10
        {"name": "Room_C",  "x": 7.0, "y": 8.2, "color": "#ef4444"}, # 70/10, 82/10
    ]


    # =====================
    # Camera
    # =====================
    camera_enabled: bool = True
    # camera_url: str = "http://10.41.145.39:5000/video_csi"
    cam_source = "gstreamer"
    cam_port = 5000           # 사용할 포트 번호
    camera_width: int = 640
    camera_height: int = 480

    # =====================
    # YOLOv5 TFLite
    # =====================
    yolo_enabled: bool = True
    yolo_model_path: str = "models/best-fp16.tflite"
    yolo_data_yaml: str = "models/data.yaml"
    yolo_labels: list[str] = None # -> 없으면 cls0, cls1 로 표시
    yolo_colors: dict[int, tuple[int,int,int]] = None
    yolo_conf_thres: float = 0.35
    yolo_nms_iou: float = 0.45

    # class-agnostic NMS 여부
    # False: per-class NMS (권장)
    # True : class-agnostic NMS (겹치면 클래스 무시하고 제거)
    yolo_nms_agnostic: bool = False

    # Overlay toggles (HMI can flip these at runtime)
    yolo_draw_boxes: bool = True
    yolo_draw_labels: bool = True

CFG = AppConfig()
