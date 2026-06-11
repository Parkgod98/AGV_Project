# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'map.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGraphicsView,
    QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSlider, QSpacerItem, QVBoxLayout,
    QWidget)
class Ui_MapPage(object):
    def setupUi(self, MapPage):
        if not MapPage.objectName():
            MapPage.setObjectName(u"MapPage")
        MapPage.resize(1100, 700)
        self.horizontalLayout_root = QHBoxLayout(MapPage)
        self.horizontalLayout_root.setSpacing(12)
        self.horizontalLayout_root.setObjectName(u"horizontalLayout_root")
        self.horizontalLayout_root.setContentsMargins(12, 12, 12, 12)
        self.group_map = QGroupBox(MapPage)
        self.group_map.setObjectName(u"group_map")
        self.verticalLayout_map = QVBoxLayout(self.group_map)
        self.verticalLayout_map.setObjectName(u"verticalLayout_map")
        self.mapView = QGraphicsView(self.group_map)
        self.mapView.setObjectName(u"mapView")
        self.mapView.setDragMode(QGraphicsView.ScrollHandDrag)

        self.verticalLayout_map.addWidget(self.mapView)

        self.horizontalLayout_mapButtons = QHBoxLayout()
        self.horizontalLayout_mapButtons.setObjectName(u"horizontalLayout_mapButtons")
        self.btn_zoom_out = QPushButton(self.group_map)
        self.btn_zoom_out.setObjectName(u"btn_zoom_out")

        self.horizontalLayout_mapButtons.addWidget(self.btn_zoom_out)

        self.btn_zoom_in = QPushButton(self.group_map)
        self.btn_zoom_in.setObjectName(u"btn_zoom_in")

        self.horizontalLayout_mapButtons.addWidget(self.btn_zoom_in)

        self.btn_fit = QPushButton(self.group_map)
        self.btn_fit.setObjectName(u"btn_fit")

        self.horizontalLayout_mapButtons.addWidget(self.btn_fit)

        self.spacer_map = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_mapButtons.addItem(self.spacer_map)

        self.lbl_zoom = QLabel(self.group_map)
        self.lbl_zoom.setObjectName(u"lbl_zoom")

        self.horizontalLayout_mapButtons.addWidget(self.lbl_zoom)

        self.sld_zoom = QSlider(self.group_map)
        self.sld_zoom.setObjectName(u"sld_zoom")
        self.sld_zoom.setOrientation(Qt.Horizontal)
        self.sld_zoom.setMinimum(20)
        self.sld_zoom.setMaximum(300)
        self.sld_zoom.setValue(100)

        self.horizontalLayout_mapButtons.addWidget(self.sld_zoom)

        self.lbl_zoom_value = QLabel(self.group_map)
        self.lbl_zoom_value.setObjectName(u"lbl_zoom_value")

        self.horizontalLayout_mapButtons.addWidget(self.lbl_zoom_value)


        self.verticalLayout_map.addLayout(self.horizontalLayout_mapButtons)


        self.horizontalLayout_root.addWidget(self.group_map)

        self.group_timeline = QGroupBox(MapPage)
        self.group_timeline.setObjectName(u"group_timeline")
        self.verticalLayout_timeline = QVBoxLayout(self.group_timeline)
        self.verticalLayout_timeline.setSpacing(10)
        self.verticalLayout_timeline.setObjectName(u"verticalLayout_timeline")
        self.horizontalLayout_mode = QHBoxLayout()
        self.horizontalLayout_mode.setObjectName(u"horizontalLayout_mode")
        self.lbl_mode = QLabel(self.group_timeline)
        self.lbl_mode.setObjectName(u"lbl_mode")

        self.horizontalLayout_mode.addWidget(self.lbl_mode)

        self.cmb_mode = QComboBox(self.group_timeline)
        self.cmb_mode.addItem("")
        self.cmb_mode.addItem("")
        self.cmb_mode.addItem("")
        self.cmb_mode.setObjectName(u"cmb_mode")

        self.horizontalLayout_mode.addWidget(self.cmb_mode)


        self.verticalLayout_timeline.addLayout(self.horizontalLayout_mode)

        self.horizontalLayout_clear = QHBoxLayout()
        self.horizontalLayout_clear.setObjectName(u"horizontalLayout_clear")
        self.btn_clear_path = QPushButton(self.group_timeline)
        self.btn_clear_path.setObjectName(u"btn_clear_path")

        self.horizontalLayout_clear.addWidget(self.btn_clear_path)

        self.lbl_poses = QLabel(self.group_timeline)
        self.lbl_poses.setObjectName(u"lbl_poses")

        self.horizontalLayout_clear.addWidget(self.lbl_poses)


        self.verticalLayout_timeline.addLayout(self.horizontalLayout_clear)

        self.horizontalLayout_tail = QHBoxLayout()
        self.horizontalLayout_tail.setObjectName(u"horizontalLayout_tail")
        self.lbl_tail = QLabel(self.group_timeline)
        self.lbl_tail.setObjectName(u"lbl_tail")

        self.horizontalLayout_tail.addWidget(self.lbl_tail)

        self.sld_tail_sec = QSlider(self.group_timeline)
        self.sld_tail_sec.setObjectName(u"sld_tail_sec")
        self.sld_tail_sec.setOrientation(Qt.Horizontal)
        self.sld_tail_sec.setMaximum(3600)
        self.sld_tail_sec.setValue(300)

        self.horizontalLayout_tail.addWidget(self.sld_tail_sec)


        self.verticalLayout_timeline.addLayout(self.horizontalLayout_tail)

        self.horizontalLayout_playback = QHBoxLayout()
        self.horizontalLayout_playback.setObjectName(u"horizontalLayout_playback")
        self.lbl_playback = QLabel(self.group_timeline)
        self.lbl_playback.setObjectName(u"lbl_playback")

        self.horizontalLayout_playback.addWidget(self.lbl_playback)

        self.chk_playback = QCheckBox(self.group_timeline)
        self.chk_playback.setObjectName(u"chk_playback")

        self.horizontalLayout_playback.addWidget(self.chk_playback)

        self.spacer_pb = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_playback.addItem(self.spacer_pb)

        self.lbl_pb_idx = QLabel(self.group_timeline)
        self.lbl_pb_idx.setObjectName(u"lbl_pb_idx")

        self.horizontalLayout_playback.addWidget(self.lbl_pb_idx)


        self.verticalLayout_timeline.addLayout(self.horizontalLayout_playback)

        self.spacer_bottom = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_timeline.addItem(self.spacer_bottom)


        self.horizontalLayout_root.addWidget(self.group_timeline)


        self.retranslateUi(MapPage)

        QMetaObject.connectSlotsByName(MapPage)
    # setupUi

    def retranslateUi(self, MapPage):
        self.group_map.setTitle(QCoreApplication.translate("MapPage", u"Robot Path Visualization", None))
        self.btn_zoom_out.setText(QCoreApplication.translate("MapPage", u"-", None))
        self.btn_zoom_in.setText(QCoreApplication.translate("MapPage", u"+", None))
        self.btn_fit.setText(QCoreApplication.translate("MapPage", u"FIT", None))
        self.lbl_zoom.setText(QCoreApplication.translate("MapPage", u"Zoom", None))
        self.lbl_zoom_value.setText(QCoreApplication.translate("MapPage", u"100%", None))
        self.group_timeline.setTitle(QCoreApplication.translate("MapPage", u"Controls", None))
        self.lbl_mode.setText(QCoreApplication.translate("MapPage", u"Mode", None))
        self.cmb_mode.setItemText(0, QCoreApplication.translate("MapPage", u"Full", None))
        self.cmb_mode.setItemText(1, QCoreApplication.translate("MapPage", u"Recent (Tail)", None))
        self.cmb_mode.setItemText(2, QCoreApplication.translate("MapPage", u"Playback", None))

        self.btn_clear_path.setText(QCoreApplication.translate("MapPage", u"Clear Trace", None))
        self.lbl_poses.setText(QCoreApplication.translate("MapPage", u"0 pts", None))
        self.lbl_tail.setText(QCoreApplication.translate("MapPage", u"Tail(s)", None))
        self.lbl_playback.setText(QCoreApplication.translate("MapPage", u"Playback", None))
        self.chk_playback.setText("")
        self.lbl_pb_idx.setText(QCoreApplication.translate("MapPage", u"0 / 0", None))
        pass
    # retranslateUi

