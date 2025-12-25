# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'control.ui'
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
from PySide6.QtWidgets import (QApplication, QDial, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSlider, QVBoxLayout, QWidget)
class Ui_ControlForm(object):
    def setupUi(self, ControlForm):
        if not ControlForm.objectName():
            ControlForm.setObjectName(u"ControlForm")
        ControlForm.resize(900, 700)
        self.horizontalLayout_root = QHBoxLayout(ControlForm)
        self.horizontalLayout_root.setObjectName(u"horizontalLayout_root")
        self.verticalLayout_left = QVBoxLayout()
        self.verticalLayout_left.setSpacing(10)
        self.verticalLayout_left.setObjectName(u"verticalLayout_left")
        self.btn_connect = QPushButton(ControlForm)
        self.btn_connect.setObjectName(u"btn_connect")
        self.btn_connect.setMinimumSize(QSize(0, 45))

        self.verticalLayout_left.addWidget(self.btn_connect)

        self.groupManualMove = QGroupBox(ControlForm)
        self.groupManualMove.setObjectName(u"groupManualMove")
        self.gl_move = QGridLayout(self.groupManualMove)
        self.gl_move.setObjectName(u"gl_move")
        self.btn_up = QPushButton(self.groupManualMove)
        self.btn_up.setObjectName(u"btn_up")

        self.gl_move.addWidget(self.btn_up, 0, 1, 1, 1)

        self.btn_left = QPushButton(self.groupManualMove)
        self.btn_left.setObjectName(u"btn_left")

        self.gl_move.addWidget(self.btn_left, 1, 0, 1, 1)

        self.btn_stop = QPushButton(self.groupManualMove)
        self.btn_stop.setObjectName(u"btn_stop")

        self.gl_move.addWidget(self.btn_stop, 1, 1, 1, 1)

        self.btn_right = QPushButton(self.groupManualMove)
        self.btn_right.setObjectName(u"btn_right")

        self.gl_move.addWidget(self.btn_right, 1, 2, 1, 1)

        self.btn_down = QPushButton(self.groupManualMove)
        self.btn_down.setObjectName(u"btn_down")

        self.gl_move.addWidget(self.btn_down, 2, 1, 1, 1)


        self.verticalLayout_left.addWidget(self.groupManualMove)

        self.hl_settings = QHBoxLayout()
        self.hl_settings.setObjectName(u"hl_settings")
        self.vboxLayout = QVBoxLayout()
        self.vboxLayout.setObjectName(u"vboxLayout")
        self.lbl_speed_title = QLabel(ControlForm)
        self.lbl_speed_title.setObjectName(u"lbl_speed_title")

        self.vboxLayout.addWidget(self.lbl_speed_title)

        self.sld_speed = QSlider(ControlForm)
        self.sld_speed.setObjectName(u"sld_speed")
        self.sld_speed.setOrientation(Qt.Horizontal)

        self.vboxLayout.addWidget(self.sld_speed)


        self.hl_settings.addLayout(self.vboxLayout)

        self.vboxLayout1 = QVBoxLayout()
        self.vboxLayout1.setObjectName(u"vboxLayout1")
        self.lbl_grab_title = QLabel(ControlForm)
        self.lbl_grab_title.setObjectName(u"lbl_grab_title")

        self.vboxLayout1.addWidget(self.lbl_grab_title)

        self.dial_grab = QDial(ControlForm)
        self.dial_grab.setObjectName(u"dial_grab")

        self.vboxLayout1.addWidget(self.dial_grab)


        self.hl_settings.addLayout(self.vboxLayout1)


        self.verticalLayout_left.addLayout(self.hl_settings)

        self.groupArmControl = QGroupBox(ControlForm)
        self.groupArmControl.setObjectName(u"groupArmControl")
        self.vl_arm = QVBoxLayout(self.groupArmControl)
        self.vl_arm.setObjectName(u"vl_arm")
        self.lbl_s1 = QLabel(self.groupArmControl)
        self.lbl_s1.setObjectName(u"lbl_s1")

        self.vl_arm.addWidget(self.lbl_s1)

        self.sld_s1 = QSlider(self.groupArmControl)
        self.sld_s1.setObjectName(u"sld_s1")
        self.sld_s1.setOrientation(Qt.Horizontal)
        self.sld_s1.setMaximum(180)

        self.vl_arm.addWidget(self.sld_s1)

        self.lbl_s2 = QLabel(self.groupArmControl)
        self.lbl_s2.setObjectName(u"lbl_s2")

        self.vl_arm.addWidget(self.lbl_s2)

        self.sld_s2 = QSlider(self.groupArmControl)
        self.sld_s2.setObjectName(u"sld_s2")
        self.sld_s2.setOrientation(Qt.Horizontal)
        self.sld_s2.setMaximum(180)

        self.vl_arm.addWidget(self.sld_s2)

        self.lbl_s3 = QLabel(self.groupArmControl)
        self.lbl_s3.setObjectName(u"lbl_s3")

        self.vl_arm.addWidget(self.lbl_s3)

        self.sld_s3 = QSlider(self.groupArmControl)
        self.sld_s3.setObjectName(u"sld_s3")
        self.sld_s3.setOrientation(Qt.Horizontal)
        self.sld_s3.setMaximum(180)

        self.vl_arm.addWidget(self.sld_s3)

        self.lbl_s4 = QLabel(self.groupArmControl)
        self.lbl_s4.setObjectName(u"lbl_s4")

        self.vl_arm.addWidget(self.lbl_s4)

        self.sld_s4 = QSlider(self.groupArmControl)
        self.sld_s4.setObjectName(u"sld_s4")
        self.sld_s4.setOrientation(Qt.Horizontal)
        self.sld_s4.setMaximum(180)

        self.vl_arm.addWidget(self.sld_s4)

        self.lbl_s5 = QLabel(self.groupArmControl)
        self.lbl_s5.setObjectName(u"lbl_s5")

        self.vl_arm.addWidget(self.lbl_s5)

        self.sld_s5 = QSlider(self.groupArmControl)
        self.sld_s5.setObjectName(u"sld_s5")
        self.sld_s5.setOrientation(Qt.Horizontal)
        self.sld_s5.setMaximum(180)

        self.vl_arm.addWidget(self.sld_s5)


        self.verticalLayout_left.addWidget(self.groupArmControl)


        self.horizontalLayout_root.addLayout(self.verticalLayout_left)

        self.frameCamera = QFrame(ControlForm)
        self.frameCamera.setObjectName(u"frameCamera")
        self.frameCamera.setMinimumSize(QSize(500, 0))
        self.frameCamera.setFrameShape(QFrame.StyledPanel)
        self.vl_cam = QVBoxLayout(self.frameCamera)
        self.vl_cam.setObjectName(u"vl_cam")
        self.lbl_camera_view = QLabel(self.frameCamera)
        self.lbl_camera_view.setObjectName(u"lbl_camera_view")
        self.lbl_camera_view.setAlignment(Qt.AlignCenter)

        self.vl_cam.addWidget(self.lbl_camera_view)


        self.horizontalLayout_root.addWidget(self.frameCamera)


        self.retranslateUi(ControlForm)

        QMetaObject.connectSlotsByName(ControlForm)
    # setupUi

    def retranslateUi(self, ControlForm):
        self.btn_connect.setText(QCoreApplication.translate("ControlForm", u"CONNECT TO AGV", None))
        self.groupManualMove.setTitle(QCoreApplication.translate("ControlForm", u"Manual Move", None))
        self.btn_up.setText(QCoreApplication.translate("ControlForm", u"\u25b2", None))
        self.btn_left.setText(QCoreApplication.translate("ControlForm", u"\u25c0", None))
        self.btn_stop.setText(QCoreApplication.translate("ControlForm", u"STOP", None))
        self.btn_right.setText(QCoreApplication.translate("ControlForm", u"\u25b6", None))
        self.btn_down.setText(QCoreApplication.translate("ControlForm", u"\u25bc", None))
        self.lbl_speed_title.setText(QCoreApplication.translate("ControlForm", u"Speed", None))
        self.lbl_grab_title.setText(QCoreApplication.translate("ControlForm", u"Grab: 0%", None))
        self.groupArmControl.setTitle(QCoreApplication.translate("ControlForm", u"Arm Servo Control", None))
        self.lbl_s1.setText(QCoreApplication.translate("ControlForm", u"S1: 90\u00b0", None))
        self.lbl_s2.setText(QCoreApplication.translate("ControlForm", u"S2: 90\u00b0", None))
        self.lbl_s3.setText(QCoreApplication.translate("ControlForm", u"S3: 90\u00b0", None))
        self.lbl_s4.setText(QCoreApplication.translate("ControlForm", u"S4: 90\u00b0", None))
        self.lbl_s5.setText(QCoreApplication.translate("ControlForm", u"S5: 90\u00b0", None))
        self.lbl_camera_view.setText(QCoreApplication.translate("ControlForm", u"Streaming URL: /video_usb ...", None))
        pass
    # retranslateUi

