from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import List, Optional

from PySide6.QtCore import Qt, QSortFilterProxyModel, QAbstractTableModel, QModelIndex, QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QPushButton,
    QFileDialog,
    QTableView,
    QLabel,
)


@dataclass
class LogRecord:
    ts_ms: int
    level: str  # INFO/WARN/ERROR/DEBUG
    source: str
    topic: str
    message: str


def _now_ms() -> int:
    return int(time.time() * 1000)


def _guess_level(msg: str) -> str:
    u = msg.upper()
    if "[ERROR]" in u or " ERROR" in u or "EXCEPTION" in u or "TRACEBACK" in u:
        return "ERROR"
    if "[WARN]" in u or " WARNING" in u:
        return "WARN"
    if "[DEBUG]" in u:
        return "DEBUG"
    return "INFO"


def _guess_source_and_topic(msg: str) -> tuple[str, str]:
    # Common patterns in this project
    #   [MQTT] ...
    #   [FS] ...
    #   [BOOT] ...
    m = re.match(r"^\[(?P<src>[^\]]+)\]\s*(?P<rest>.*)$", msg.strip())
    if m:
        src = m.group("src")
        rest = m.group("rest")
        # Extract topic if present: "topic -> payload" or "SUB <topic>"
        topic = ""
        mm = re.search(r"(\/[^\s]+|[a-zA-Z0-9_\-/\+]+\/[^\s]+)\s*->", rest)
        if mm:
            topic = mm.group(1)
        else:
            mm = re.search(r"\bSUB\s+([^\s]+)", rest)
            if mm:
                topic = mm.group(1)
        return src, topic
    return "APP", ""


class _LogTableModel(QAbstractTableModel):
    COLS = ["Time", "Level", "Source", "Topic", "Message"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows: List[LogRecord] = []

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.COLS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self.COLS[section]
        return str(section)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        r = self.rows[index.row()]
        c = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if c == 0:
                # HH:MM:SS.mmm
                t = r.ts_ms
                lt = time.localtime(t / 1000.0)
                ms = t % 1000
                return time.strftime("%H:%M:%S", lt) + f".{ms:03d}"
            if c == 1:
                return r.level
            if c == 2:
                return r.source
            if c == 3:
                return r.topic
            if c == 4:
                return r.message

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if c in (0, 1, 2, 3):
                return int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            return int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        if role == Qt.ItemDataRole.UserRole:
            # for proxy filtering
            return r

        if role == Qt.ItemDataRole.ForegroundRole:
            r = self.rows[index.row()]
            if r.level == "ERROR": return QColor("#ef4444") # Red
            if r.level == "WARN":  return QColor("#eab308") # Yellow
            if r.level == "DEBUG": return QColor("#94a3b8") # Grey
            return QColor("#3b82f6") # INFO - Blue

        return None

    def append(self, rec: LogRecord, max_keep: int = 5000):
        # drop oldest when too large
        if len(self.rows) >= max_keep:
            drop = len(self.rows) - max_keep + 1
            self.beginRemoveRows(QModelIndex(), 0, drop - 1)
            self.rows = self.rows[drop:]
            self.endRemoveRows()

        self.beginInsertRows(QModelIndex(), len(self.rows), len(self.rows))
        self.rows.append(rec)
        self.endInsertRows()


class _LogFilterProxy(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.level_min = "INFO"
        self.q = ""
        self.topic_q = ""
        self._levels = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3}

    def set_level_min(self, level: str):
        self.level_min = level
        self.invalidateFilter()

    def set_query(self, q: str):
        self.q = (q or "").strip().lower()
        self.invalidateFilter()

    def set_topic_query(self, q: str):
        self.topic_q = (q or "").strip().lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex):
        m = self.sourceModel()
        idx = m.index(source_row, 0, source_parent)
        rec: LogRecord = m.data(idx, Qt.ItemDataRole.UserRole)
        if rec is None:
            return True

        if self._levels.get(rec.level, 1) < self._levels.get(self.level_min, 1):
            return False

        if self.topic_q:
            if self.topic_q not in (rec.topic or "").lower() and self.topic_q not in rec.message.lower():
                return False

        if self.q:
            blob = f"{rec.level} {rec.source} {rec.topic} {rec.message}".lower()
            return self.q in blob
        return True


class LogsPageV8(QWidget):
    """Operator-friendly logs page.

    - Search + severity filter + topic filter
    - Auto-scroll toggle
    - Clear + Export

    Compatibility: MainWindow expects `.append(str)`.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # top controls
        top = QHBoxLayout()
        top.setSpacing(8)

        top.addWidget(QLabel("Level"))
        self.cmb_level = QComboBox()
        self.cmb_level.addItems(["DEBUG", "INFO", "WARN", "ERROR"])
        self.cmb_level.setCurrentText("INFO")
        top.addWidget(self.cmb_level)

        top.addWidget(QLabel("Search"))
        self.ed_search = QLineEdit()
        self.ed_search.setPlaceholderText("message/source/topic")
        top.addWidget(self.ed_search, 1)

        top.addWidget(QLabel("Topic"))
        self.ed_topic = QLineEdit()
        self.ed_topic.setPlaceholderText("/robot/... or cmd/... (optional)")
        top.addWidget(self.ed_topic, 1)

        self.chk_autoscroll = QCheckBox("Auto-scroll")
        self.chk_autoscroll.setChecked(True)
        top.addWidget(self.chk_autoscroll)

        self.btn_export = QPushButton("Export")
        self.btn_clear = QPushButton("Clear")
        top.addWidget(self.btn_export)
        top.addWidget(self.btn_clear)

        root.addLayout(top)

        # table
        self.table = QTableView()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.setSortingEnabled(True)

        self.model = _LogTableModel(self)
        self.proxy = _LogFilterProxy(self)
        self.proxy.setSourceModel(self.model)
        self.table.setModel(self.proxy)

        # column widths
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 70)
        self.table.setColumnWidth(2, 90)
        self.table.setColumnWidth(3, 250)
        self.table.horizontalHeader().setStretchLastSection(True)

        root.addWidget(self.table, 1)

        # wiring
        self.btn_clear.clicked.connect(self.clear)
        self.btn_export.clicked.connect(self.export)
        self.cmb_level.currentTextChanged.connect(self.proxy.set_level_min)
        self.ed_search.textChanged.connect(self.proxy.set_query)
        self.ed_topic.textChanged.connect(self.proxy.set_topic_query)

        # init filter
        self.proxy.set_level_min(self.cmb_level.currentText())

    # ---------- API ----------
    def append(self, msg: str):
        msg = str(msg)
        level = _guess_level(msg)
        src, topic = _guess_source_and_topic(msg)
        rec = LogRecord(ts_ms=_now_ms(), level=level, source=src, topic=topic, message=msg)
        self.model.append(rec)

        if self.chk_autoscroll.isChecked():
            # scroll to bottom (last visible row in proxy)
            last_row = self.proxy.rowCount() - 1
            if last_row >= 0:
                self.table.scrollTo(self.proxy.index(last_row, 0))

    def clear(self):
        self.model.beginResetModel()
        self.model.rows = []
        self.model.endResetModel()

    def export(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export logs", "logs.txt", "Text (*.txt)")
        if not path:
            return
        # Export current filtered view
        lines: List[str] = []
        for r in range(self.proxy.rowCount()):
            idx0 = self.proxy.index(r, 0)
            idx1 = self.proxy.index(r, 1)
            idx2 = self.proxy.index(r, 2)
            idx3 = self.proxy.index(r, 3)
            idx4 = self.proxy.index(r, 4)
            t = self.proxy.data(idx0, Qt.ItemDataRole.DisplayRole)
            lv = self.proxy.data(idx1, Qt.ItemDataRole.DisplayRole)
            src = self.proxy.data(idx2, Qt.ItemDataRole.DisplayRole)
            tp = self.proxy.data(idx3, Qt.ItemDataRole.DisplayRole)
            ms = self.proxy.data(idx4, Qt.ItemDataRole.DisplayRole)
            lines.append(f"{t}\t{lv}\t{src}\t{tp}\t{ms}")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
