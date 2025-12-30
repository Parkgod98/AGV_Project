# utils/map_view.py
from __future__ import annotations
import math

from PySide6.QtCore import Qt, QPointF, Property
from PySide6.QtGui import (
    QPen, QPainterPath, QPainter,
    QColor, QBrush
)
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsLineItem
)


class MapView(QGraphicsView):
    """
    가상 맵(QGraphicsView)
    - 색/테마는 QSS(qproperty-*)에서 관리
    - 이 클래스는 '읽어서 적용'만 담당
    """

    def __init__(self, world_w_m=10.0, world_h_m=10.0, px_per_m=80.0, parent=None):
        super().__init__(parent)

        # 최초 1회 auto-fit (맵 전체를 현재 위젯 크기에 맞춰서 보여주기)
        self._did_autofit = False

        # ---------- identity (QSS target) ----------
        self.setObjectName("mapView")

        # QSS-settable property tokens
        self.__init_qss_props()

        # ---------- world params ----------
        self.world_w_m = float(world_w_m)
        self.world_h_m = float(world_h_m)
        self.px_per_m = float(px_per_m)

        # ---------- scene ----------
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self.scene_w = self.world_w_m * self.px_per_m
        self.scene_h = self.world_h_m * self.px_per_m
        self._scene.setSceneRect(0, 0, self.scene_w, self.scene_h)

        # ---------- view behavior ----------
        self.setRenderHints(self.renderHints() | QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        # dashboard 느낌: 스크롤바 숨김 (드래그/휠 줌은 유지)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # ---------- theme from QSS ----------
        self._apply_theme_from_qss()

        # ---------- grid ----------
        self._draw_grid(grid_m=1.0)

        # ---------- robot ----------
        self._init_robot()

        # ---------- trajectory ----------
        self._init_traj()


    # ==================================================
    # Qt properties (so QSS qproperty-* does not warn)
    # ==================================================
    def __init_qss_props(self):
        self._sceneBg = ""
        self._gridColor = ""
        self._borderColor = ""
        self._pathColor = ""
        self._robotColor = ""

    def _get_sceneBg(self):
        return self._sceneBg

    def _set_sceneBg(self, v):
        self._sceneBg = str(v)

    sceneBg = Property(str, _get_sceneBg, _set_sceneBg)

    def _get_gridColor(self):
        return self._gridColor

    def _set_gridColor(self, v):
        self._gridColor = str(v)

    gridColor = Property(str, _get_gridColor, _set_gridColor)

    def _get_borderColor(self):
        return self._borderColor

    def _set_borderColor(self, v):
        self._borderColor = str(v)

    borderColor = Property(str, _get_borderColor, _set_borderColor)

    def _get_pathColor(self):
        return self._pathColor

    def _set_pathColor(self, v):
        self._pathColor = str(v)

    pathColor = Property(str, _get_pathColor, _set_pathColor)

    def _get_robotColor(self):
        return self._robotColor

    def _set_robotColor(self, v):
        self._robotColor = str(v)

    robotColor = Property(str, _get_robotColor, _set_robotColor)

    # ==================================================
    # QSS THEME
    # ==================================================
    def _qcolor(self, prop: str, fallback: str) -> QColor:
        """
        QSS의 qproperty-* 값을 QColor로 변환
        """
        v = self.property(prop)
        if isinstance(v, QColor):
            return v
        if v is None:
            return QColor(fallback)
        return QColor(str(v))

    def _apply_theme_from_qss(self):
        self._scene_bg   = self._qcolor("sceneBg", "#0b0e14")
        self._grid_c     = self._qcolor("gridColor", "#222a38")
        self._border_c   = self._qcolor("borderColor", "#d7dbe0")
        self._path_c     = self._qcolor("pathColor", "#e7eaf0")
        self._robot_c    = self._qcolor("robotColor", "#ffffff")

        self._scene.setBackgroundBrush(QBrush(self._scene_bg))

    # ==================================================
    # DRAWING
    # ==================================================
    def _draw_grid(self, grid_m=1.0):
        step = grid_m * self.px_per_m

        # grid_pen = QPen(self._grid_c, 1)
        # grid_pen.setCosmetic(True)

        border_pen = QPen(self._border_c, 2)
        border_pen.setCosmetic(True)

        # border
        self._scene.addRect(0, 0, self.scene_w, self.scene_h, border_pen)

        # grid lines
        x = 0.0
        while x <= self.scene_w:
            self._scene.addLine(x, 0, x, self.scene_h, grid_pen)
            x += step

        y = 0.0
        while y <= self.scene_h:
            self._scene.addLine(0, y, self.scene_w, y, grid_pen)
            y += step

    def _init_robot(self):
        r_px = 7

        self.robot_dot = QGraphicsEllipseItem(-r_px, -r_px, 2 * r_px, 2 * r_px)
        self.robot_dot.setPen(QPen(self._robot_c, 2))
        self.robot_dot.setBrush(QBrush(self._robot_c))
        self._scene.addItem(self.robot_dot)

        self.heading = QGraphicsLineItem(0, 0, 28, 0)
        head_pen = QPen(self._robot_c, 3)
        head_pen.setCosmetic(True)
        self.heading.setPen(head_pen)
        self._scene.addItem(self.heading)

    def _init_traj(self):
        self.traj_item = QGraphicsPathItem()
        traj_pen = QPen(self._path_c, 2)
        traj_pen.setCosmetic(True)
        self.traj_item.setPen(traj_pen)
        self._scene.addItem(self.traj_item)
        self._traj_path = QPainterPath()

    # ==================================================
    # COORD / UPDATE
    # ==================================================
    def meters_to_scene(self, x_m: float, y_m: float) -> QPointF:
        x_px = x_m * self.px_per_m
        y_px = (self.world_h_m - y_m) * self.px_per_m
        return QPointF(x_px, y_px)

    def update_pose(self, x_m: float, y_m: float, yaw_rad: float):
        p = self.meters_to_scene(x_m, y_m)
        self.robot_dot.setPos(p)
        self.heading.setPos(p)
        self.heading.setRotation(-math.degrees(yaw_rad))

    def set_traj_points(self, points_xy_m: list[tuple[float, float]]):
        self._traj_path = QPainterPath()
        if not points_xy_m:
            self.traj_item.setPath(self._traj_path)
            return

        p0 = self.meters_to_scene(points_xy_m[0][0], points_xy_m[0][1])
        self._traj_path.moveTo(p0)

        for x_m, y_m in points_xy_m[1:]:
            p = self.meters_to_scene(x_m, y_m)
            self._traj_path.lineTo(p)

        self.traj_item.setPath(self._traj_path)

    def clear_traj(self):
        self._traj_path = QPainterPath()
        self.traj_item.setPath(self._traj_path)

    # ==================================================
    # ZOOM
    # ==================================================
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.scale(1.15, 1.15)
        else:
            self.scale(1 / 1.15, 1 / 1.15)

    # ==================================================
    # AUTO-FIT (1회)
    # ==================================================
    def fit_to_world(self):
        """Fit entire world (sceneRect) into current view once."""
        rect = self.scene().sceneRect()
        if rect.isNull() or rect.width() <= 0 or rect.height() <= 0:
            rect = self.scene().itemsBoundingRect()
        if rect.isNull() or rect.width() <= 0 or rect.height() <= 0:
            return

        rect = rect.adjusted(-8, -8, 8, 8)  # small padding in px
        self.fitInView(rect, Qt.KeepAspectRatio)
        self._did_autofit = True

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if not self._did_autofit:
            self.fit_to_world()
