# utils/yolo_labels.py
import yaml

def load_labels_from_data_yaml(path: str):
    """
    data.yaml 예:
    names:
      0: laundry
      1: water
    colors:
      0: [0, 200, 0]   # BGR
      1: [255, 0, 0]
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"[WARN] failed to load data.yaml: {e}")
        return None, None

    # ---------- labels ----------
    labels = None
    names = data.get("names", None)
    if isinstance(names, dict):
        labels = [names[k] for k in sorted(names.keys())]
    elif isinstance(names, list):
        labels = names

    # ---------- colors ----------
    colors = None
    raw_colors = data.get("colors", None)
    if isinstance(raw_colors, dict):
        # key가 str로 들어올 수 있어서 int 캐스팅
        colors = {int(k): tuple(v) for k, v in raw_colors.items()}

    return labels, colors
