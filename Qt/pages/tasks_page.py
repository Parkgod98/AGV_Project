from __future__ import annotations
import time
from typing import Any, Dict, List, Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QFrame, QSplitter, QLineEdit, QComboBox,
)

# --- 헬퍼 함수들 (보내주신 코드 유지) ---
def _fmt_ms(ms: Any) -> str:
    try:
        v = float(ms)
        if v >= 1000: return f"{v/1000.0:.2f}s"
        return f"{v:.0f}"
    except: return ""

def _ts_to_hms(ts: Any) -> str:
    try:
        v = float(ts)
        if v > 1e11: v = v / 1000.0
        lt = time.localtime(v)
        return time.strftime("%m-%d %H:%M:%S", lt)
    except: return ""

def _status_badge(status: str) -> str:
    s = (status or "").lower()
    if s in ("fail", "failed", "error"): return "❌"
    if s in ("done", "success", "completed", "complete"): return "✅"
    if s in ("running", "in_progress", "executing"): return "▶"
    if s in ("queued", "pending"): return "⏳"
    return "•"

# --- 메인 클래스 (MainWindow와 연동을 위해 이름만 TasksPage로 변경) ---
class TasksPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._tasks_by_id: Dict[str, Dict[str, Any]] = {}
        self._interactions_by_id: Dict[str, Dict[str, Any]] = {}
        self._events_by_task: Dict[str, List[Dict[str, Any]]] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # Filters 영역
        flt = QHBoxLayout()
        flt.setSpacing(8)
        flt.addWidget(QLabel("Status"))
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["ALL", "queued", "running", "done", "fail"])
        flt.addWidget(self.cmb_status)

        flt.addWidget(QLabel("Search"))
        self.ed_search = QLineEdit()
        self.ed_search.setPlaceholderText("task_id / type / target / robot")
        flt.addWidget(self.ed_search, 1)
        root.addLayout(flt)

        # Splitter (Master-Detail 구조)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Master List
        left = QFrame()
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(0, 0, 0, 0)
        left_l.setSpacing(6)
        self.lbl_left = QLabel("Tasks")
        left_l.addWidget(self.lbl_left)
        self.list = QListWidget()
        self.list.setUniformItemSizes(True)
        left_l.addWidget(self.list, 1)
        self.splitter.addWidget(left)

        # Right: Detail
        right = QFrame()
        right_l = QVBoxLayout(right)
        right_l.setContentsMargins(0, 0, 0, 0)
        right_l.setSpacing(6)

        self.lbl_detail = QLabel("Select a task to see details")
        self.lbl_detail.setWordWrap(True)
        self.lbl_detail.setStyleSheet("background: #1e2a38; padding: 10px; border-radius: 5px;")
        right_l.addWidget(self.lbl_detail)

        self.lbl_interaction = QLabel("")
        self.lbl_interaction.setWordWrap(True)
        self.lbl_interaction.setStyleSheet("color: #aaa; padding: 5px;")
        right_l.addWidget(self.lbl_interaction)

        right_l.addWidget(QLabel("Events"))
        self.events = QListWidget()
        right_l.addWidget(self.events, 1)

        self.splitter.addWidget(right)
        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 3)
        root.addWidget(self.splitter, 1)

        # Wiring (이벤트 연결)
        self.list.currentItemChanged.connect(self._on_selected)
        self.ed_search.textChanged.connect(lambda _: self._rebuild_list())
        self.cmb_status.currentTextChanged.connect(lambda _: self._rebuild_list())

        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet("QSplitter::handle { background: #222a38; }")

    # --- Data Setters (MainWindow에서 호출하는 함수들) ---
    def set_tasks(self, tasks: list):
        self._tasks_by_id = {}
        for t in tasks or []:
            tid = str(t.get("task_id") or t.get("_id") or "")
            if tid: self._tasks_by_id[tid] = t
        self._rebuild_list(keep_selection=True)

    def set_interactions(self, interactions: list):
        self._interactions_by_id = {}
        for it in interactions or []:
            iid = str(it.get("interaction_id") or it.get("_id") or "")
            if iid: self._interactions_by_id[iid] = it
        self._refresh_detail()

    def set_events(self, events: list):
        self._events_by_task = {}
        for ev in events or []:
            tid = str(ev.get("task_id") or "")
            if tid: self._events_by_task.setdefault(tid, []).append(ev)
        self._refresh_detail()

    # --- Logic & UI Update ---
    def _task_sort_key(self, t: Dict[str, Any]) -> float:
        for k in ("created_at", "ts", "started_at", "finished_at"):
            v = t.get(k)
            try:
                if v is not None: return -float(v)
            except: pass
        return 0.0

    def _match_filters(self, t: Dict[str, Any]) -> bool:
        st_f = self.cmb_status.currentText().lower()
        st = str(t.get("status", "")).lower()
        if st_f != "all":
            if st_f == "done" and st not in ("done", "success", "completed", "complete"): return False
            if st_f == "fail" and st not in ("fail", "failed", "error"): return False
            if st_f == "running" and st not in ("running", "in_progress", "executing"): return False
            if st_f == "queued" and st not in ("queued", "pending"): return False

        q = self.ed_search.text().strip().lower()
        if q:
            blob = " ".join([str(t.get("task_id","")), str(t.get("type","")),
                             str(t.get("target_area","")), str(t.get("assigned_robot",""))]).lower()
            if q not in blob: return False
        return True

    def _rebuild_list(self, keep_selection: bool = False):
        cur_id = None
        if keep_selection:
            it = self.list.currentItem()
            if it: cur_id = it.data(Qt.ItemDataRole.UserRole)

        self.list.blockSignals(True)
        self.list.clear()

        tasks = [t for t in self._tasks_by_id.values() if self._match_filters(t)]
        tasks = sorted(tasks, key=self._task_sort_key)

        for t in tasks:
            tid = str(t.get("task_id") or t.get("_id") or "")
            badge = _status_badge(str(t.get("status", "")))
            ttype = str(t.get("type", ""))
            target = str(t.get("target_area", ""))
            robot = str(t.get("assigned_robot", ""))
            created = _ts_to_hms(t.get("created_at") or t.get("ts") or "")
            txt = f"{badge} {created}  {ttype} → {target}  ({robot})\n{tid}"
            item = QListWidgetItem(txt)
            item.setData(Qt.ItemDataRole.UserRole, tid)
            self.list.addItem(item)

        self.lbl_left.setText(f"Tasks ({len(tasks)})")
        self.list.blockSignals(False)

        if cur_id:
            for i in range(self.list.count()):
                if self.list.item(i).data(Qt.ItemDataRole.UserRole) == cur_id:
                    self.list.setCurrentRow(i)
                    break
        elif self.list.count() > 0:
            self.list.setCurrentRow(0)

    def _selected_task_id(self) -> Optional[str]:
        it = self.list.currentItem()
        return str(it.data(Qt.ItemDataRole.UserRole)) if it else None

    def _on_selected(self, *_):
        self._refresh_detail()

    def _refresh_detail(self):
        tid = self._selected_task_id()
        if not tid:
            self.lbl_detail.setText("Select a task to see details")
            self.lbl_interaction.setText(""); self.events.clear()
            return

        t = self._tasks_by_id.get(tid, {})
        parts = [f"<b>task_id:</b> {tid}", f"<b>type:</b> {t.get('type','')}",
                 f"<b>status:</b> {t.get('status','')}", f"<b>target:</b> {t.get('target_area','')}"]
        if t.get("assigned_robot"): parts.append(f"<b>robot:</b> {t.get('assigned_robot','')}")
        exp = _fmt_ms(t.get("expected_duration_ms", "")); act = _fmt_ms(t.get("actual_duration_ms", ""))
        if exp or act: parts.append(f"<b>duration:</b> expected={exp} / actual={act}")
        self.lbl_detail.setText("<br>".join(parts))

        iid = str(t.get("interaction_id") or "")
        if iid:
            it = self._interactions_by_id.get(iid, {})
            self.lbl_interaction.setText(f"interaction: id={iid} | source={it.get('source','')} | user={it.get('user_id','')}")
        else: self.lbl_interaction.setText("interaction: -")

        self.events.clear()
        evs = sorted(self._events_by_task.get(tid, []), key=lambda e: -float(e.get("ts", 0)))
        for e in evs:
            ts = _ts_to_hms(e.get("ts", ""))
            st = str(e.get("state", e.get("type", "")))
            msg = str(e.get("msg", e.get("detail", "")))
            self.events.addItem(f"{ts}  {st}  {msg}")
