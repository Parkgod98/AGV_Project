# vision/yolov5_tflite_worker.py
import cv2
import time
import numpy as np

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage, QPixmap

try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    from tensorflow.lite.python.interpreter import Interpreter


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
    """class-agnostic NMS"""
    if not dets:
        return []
    dets = np.asarray(dets, dtype=np.float32)
    boxes = dets[:, :4]
    scores = dets[:, 4]
    order = scores.argsort()[::-1]
    keep = []
    while order.size > 0:
        i = int(order[0])
        keep.append(i)
        if order.size == 1:
            break
        ious = _bbox_iou_xyxy(boxes[i], boxes[order[1:]])
        inds = np.where(ious <= iou_thres)[0]
        order = order[inds + 1]
    return dets[keep].tolist()


def nms_xyxy_per_class(dets, iou_thres=0.45):
    """per-class NMS"""
    if not dets:
        return []
    dets = np.asarray(dets, dtype=np.float32)
    out = []
    cls_ids = dets[:, 5].astype(np.int32)
    for c in np.unique(cls_ids):
        part = dets[cls_ids == c].tolist()
        out.extend(nms_xyxy(part, iou_thres=iou_thres))
    return out


class YoloTFLiteWorker(QThread):
    frameReady = Signal(QPixmap)
    status = Signal(str)

    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.running = False

        self.interpreter = Interpreter(model_path=cfg.yolo_model_path)
        self.interpreter.allocate_tensors()

        self.input_detail = self.interpreter.get_input_details()[0]
        self.output_details = self.interpreter.get_output_details()

        in_shape = self.input_detail["shape"]
        _, self.in_h, self.in_w, _ = in_shape
        self.float_input = (self.input_detail["dtype"] == np.float32)

        self.status.emit(f"[TFLite] input={tuple(in_shape)} dtype={self.input_detail['dtype']}")

    def stop(self):
        self.running = False

    def preprocess(self, frame):
        img = cv2.resize(frame, (self.in_w, self.in_h))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0 if self.float_input else img
        return np.expand_dims(img, axis=0)

    def to_qpixmap(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        return QPixmap.fromImage(QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888))

    def parse_out_as_raw(self, out, frame_w, frame_h):
        """
        raw 형태 가정: [cx,cy,w,h,obj,cls...]
        """
        dets = []
        arr = np.array(out)
        if arr.ndim == 3 and arr.shape[0] == 1:
            arr = arr[0]
        if arr.ndim != 2:
            arr = arr.reshape(-1, arr.shape[-1])

        for row in arr:
            obj = float(row[4])
            if obj < self.cfg.yolo_conf_thres:
                continue

            cx, cy, ww, hh = row[:4].astype(np.float32)

            # ✅ (수정1) 좌표 스케일 강제 통일: "항상 normalized"라고 가정하고 픽셀로 변환
            cx *= frame_w
            ww *= frame_w
            cy *= frame_h
            hh *= frame_h

            x1 = cx - ww / 2.0
            y1 = cy - hh / 2.0
            x2 = cx + ww / 2.0
            y2 = cy + hh / 2.0

            cls_scores = row[5:]
            cls_id = int(np.argmax(cls_scores)) if cls_scores.size else 0

            # ✅ (수정2) score는 obj만 사용 (NMS가 확실히 먹게)
            score = obj

            dets.append([x1, y1, x2, y2, score, cls_id])

        return dets

    def parse_out_as_nmsed(self, out, frame_w, frame_h):
        """
        (N,6) 형태 가정: [x1,y1,x2,y2,score,cls]
        """
        dets = []
        arr = np.array(out)
        if arr.ndim == 3 and arr.shape[0] == 1:
            arr = arr[0]
        if arr.ndim != 2:
            arr = arr.reshape(-1, arr.shape[-1])

        if arr.shape[1] != 6:
            return []

        xyxy = arr[:, :4].astype(np.float32)
        score = arr[:, 4].astype(np.float32)
        clsid = arr[:, 5].astype(np.float32)

        # 0~1 좌표면 픽셀로
        if float(np.max(xyxy)) <= 1.5:
            xyxy[:, [0, 2]] *= frame_w
            xyxy[:, [1, 3]] *= frame_h

        for i in range(arr.shape[0]):
            if float(score[i]) < self.cfg.yolo_conf_thres:
                continue
            dets.append([xyxy[i,0], xyxy[i,1], xyxy[i,2], xyxy[i,3], float(score[i]), int(clsid[i])])

        return dets

    def draw_boxes(self, frame, dets):
        H, W = frame.shape[:2]
        labels = getattr(self.cfg, "yolo_labels", None)
        colors = getattr(self.cfg, "yolo_colors", None)

        draw_boxes = bool(getattr(self.cfg, "yolo_draw_boxes", True))
        draw_labels = bool(getattr(self.cfg, "yolo_draw_labels", True))

        for x1, y1, x2, y2, score, cls_id in dets:
            cid = int(cls_id)
            x1 = int(np.clip(x1, 0, W - 1))
            y1 = int(np.clip(y1, 0, H - 1))
            x2 = int(np.clip(x2, 0, W - 1))
            y2 = int(np.clip(y2, 0, H - 1))

            color = (0, 255, 0)
            if isinstance(colors, dict):
                color = colors.get(cid, color)

            if isinstance(labels, list) and 0 <= cid < len(labels):
                name = labels[cid]
            else:
                name = f"cls{cid}"

            if draw_boxes:
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            if draw_labels:
                cv2.putText(
                    frame,
                    f"{name} {score:.2f}",
                    (x1, max(0, y1 - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2,
                )

        return frame

    def run(self):
        cap = cv2.VideoCapture(self.cfg.camera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cfg.camera_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cfg.camera_height)

        if not cap.isOpened():
            self.status.emit("Camera open failed")
            return

        self.running = True
        self.status.emit("YOLO camera started")

        # IoU threshold 가져오기: yolo_nms_iou 우선, 없으면 yolo_iou_thres fallback
        nms_iou = getattr(self.cfg, "yolo_nms_iou", None)
        if nms_iou is None:
            nms_iou = getattr(self.cfg, "yolo_iou_thres", 0.45)

        # agnostic 스위치 (없으면 False)
        agnostic = bool(getattr(self.cfg, "yolo_nms_agnostic", False))

        while self.running:
            ret, frame = cap.read()
            if not ret or frame is None:
                continue

            inp = self.preprocess(frame)
            self.interpreter.set_tensor(self.input_detail["index"], inp)
            self.interpreter.invoke()

            out0 = self.interpreter.get_tensor(self.output_details[0]["index"])
            H, W = frame.shape[:2]

            # 출력 포맷 추정
            arr = np.array(out0)
            if arr.ndim == 3 and arr.shape[0] == 1:
                arr2 = arr[0]
            else:
                arr2 = arr.reshape(-1, arr.shape[-1])

            D = arr2.shape[1]
            if D == 6:
                dets = self.parse_out_as_nmsed(arr2, W, H)
            else:
                dets = self.parse_out_as_raw(arr2, W, H)

            # ✅ (수정3) NMS 적용 (여기 없어서 지금까지 “NMS 안 되는 것처럼” 보였던 거)
            if dets:
                # 디버그 보고 싶으면 주석 해제
                # print(f"[DEBUG] before NMS: {len(dets)}")

                if agnostic:
                    dets = nms_xyxy(dets, iou_thres=nms_iou)
                else:
                    dets = nms_xyxy_per_class(dets, iou_thres=nms_iou)

                # print(f"[DEBUG] after NMS: {len(dets)}")

            frame = self.draw_boxes(frame, dets)
            self.frameReady.emit(self.to_qpixmap(frame))

            time.sleep(0.03)

        cap.release()
        self.status.emit("YOLO camera stopped")

