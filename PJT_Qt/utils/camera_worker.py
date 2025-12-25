import cv2
import numpy as np
import time
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QImage, QPixmap

try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    from tensorflow.lite.python.interpreter import Interpreter

# ==========================================
# 1. 후처리용 NMS 함수 (기존 로직 유지)
# ==========================================
def _bbox_iou_xyxy(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b[..., 0], b[..., 1], b[..., 2], b[..., 3]
    inter_x1 = np.maximum(ax1, bx1)
    inter_y1 = np.maximum(ay1, by1)
    inter_x2 = np.minimum(ax2, bx2)
    inter_y2 = np.minimum(ay2, by2)
    inter_w = np.maximum(0.0, inter_x2 - inter_x1)
    inter_h = np.maximum(0.0, inter_y2 - inter_y1)
    inter = inter_w * inter_h
    area_a = np.maximum(0.0, ax2 - ax1) * np.maximum(0.0, ay2 - ay1)
    area_b = np.maximum(0.0, bx2 - bx1) * np.maximum(0.0, by2 - by1)
    return inter / (area_a + area_b - inter + 1e-9)

def nms_xyxy(dets, iou_thres=0.45):
    if not dets: return []
    dets = np.asarray(dets, dtype=np.float32)
    boxes = dets[:, :4]
    scores = dets[:, 4]
    order = scores.argsort()[::-1]
    keep = []
    while order.size > 0:
        i = int(order[0])
        keep.append(i)
        if order.size == 1: break
        ious = _bbox_iou_xyxy(boxes[i], boxes[order[1:]])
        inds = np.where(ious <= iou_thres)[0]
        order = order[inds + 1]
    return dets[keep].tolist()

# ==========================================
# 2. 통합 카메라 & 추론 워커
# ==========================================
class CameraWorker(QThread):
    frameReady = Signal(QPixmap)
    status = Signal(str)

    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.running = False

        # TFLite 모델 초기화
        try:
            self.interpreter = Interpreter(model_path=cfg.yolo_model_path)
            self.interpreter.allocate_tensors()
            self.input_detail = self.interpreter.get_input_details()[0]
            self.output_details = self.interpreter.get_output_details()
            _, self.in_h, self.in_w, _ = self.input_detail["shape"]
            self.status.emit(f"YOLO Model Loaded: {cfg.yolo_model_path}")
        except Exception as e:
            self.status.emit(f"Model Load Error: {e}")

    def preprocess(self, frame):
        img = cv2.resize(frame, (self.in_w, self.in_h))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0
        return np.expand_dims(img, axis=0)

    def parse_outputs(self, out, frame_w, frame_h):
        dets = []
        arr = np.array(out)
        if arr.ndim == 3: arr = arr[0]

        for row in arr:
            obj_conf = float(row[4])
            if obj_conf < self.cfg.yolo_conf_thres: continue

            # 중앙 좌표 기반 -> xyxy 변환
            cx, cy, w, h = row[:4]
            x1 = (cx - w / 2) * frame_w
            y1 = (cy - h / 2) * frame_h
            x2 = (cx + w / 2) * frame_w
            y2 = (cy + h / 2) * frame_h

            cls_id = int(np.argmax(row[5:]))
            dets.append([x1, y1, x2, y2, obj_conf, cls_id])
        return dets

    def draw_boxes(self, frame, dets):
        for x1, y1, x2, y2, score, cls_id in dets:
            color = (0, 255, 0) # Green
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            label = f"ID:{int(cls_id)} {score:.2f}"
            cv2.putText(frame, label, (int(x1), int(y1)-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return frame

    def run(self):
        # 젯슨 나노 GStreamer 수신 (포트 5000)
        pipeline = (
            "udpsrc port=5000 ! "
            "application/x-rtp, payload=96 ! "
            "rtph264depay ! avdec_h264 ! "
            "videoconvert ! appsink drop=true"
        )
        cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

        if not cap.isOpened():
            self.status.emit("GStreamer Connection Failed (Port 5000)")
            return

        self.running = True
        while self.running:
            ret, frame = cap.read()
            if not ret or frame is None: continue

            # 1. 추론 전처리
            inp = self.preprocess(frame)

            # 2. 모델 추론
            self.interpreter.set_tensor(self.input_detail["index"], inp)
            self.interpreter.invoke()

            # 3. 결과 파싱 및 NMS
            raw_out = self.interpreter.get_tensor(self.output_details[0]["index"])
            dets = self.parse_outputs(raw_out, frame.shape[1], frame.shape[0])
            dets = nms_xyxy(dets, iou_thres=getattr(self.cfg, "yolo_iou_thres", 0.45))

            # 4. 박스 그리기
            frame = self.draw_boxes(frame, dets)

            # 5. QPixmap 변환 및 송출
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.frameReady.emit(QPixmap.fromImage(qimg))

        cap.release()
