# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'overview.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_OverviewForm(object):
    def setupUi(self, OverviewForm):
        if not OverviewForm.objectName():
            OverviewForm.setObjectName(u"OverviewForm")
        OverviewForm.resize(952, 520)
        self.vl_root = QVBoxLayout(OverviewForm)
        self.vl_root.setSpacing(12)
        self.vl_root.setObjectName(u"vl_root")
        self.vl_root.setContentsMargins(16, 12, 16, 16)
        self.frame_status_bar = QFrame(OverviewForm)
        self.frame_status_bar.setObjectName(u"frame_status_bar")
        self.frame_status_bar.setMinimumSize(QSize(0, 45))
        self.frame_status_bar.setFrameShape(QFrame.Shape.StyledPanel)
        self.hl_status = QHBoxLayout(self.frame_status_bar)
        self.hl_status.setObjectName(u"hl_status")
        self.hl_status.setContentsMargins(15, -1, 15, -1)
        self.lbl_robot_id = QLabel(self.frame_status_bar)
        self.lbl_robot_id.setObjectName(u"lbl_robot_id")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.lbl_robot_id.setFont(font)

        self.hl_status.addWidget(self.lbl_robot_id)

        self.spacer_status = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hl_status.addItem(self.spacer_status)


        self.vl_root.addWidget(self.frame_status_bar)

        self.grid_cards_2x2 = QGridLayout()
        self.grid_cards_2x2.setSpacing(16)
        self.grid_cards_2x2.setObjectName(u"grid_cards_2x2")
        self.card_batt = QFrame(OverviewForm)
        self.card_batt.setObjectName(u"card_batt")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.card_batt.sizePolicy().hasHeightForWidth())
        self.card_batt.setSizePolicy(sizePolicy)
        self.vl_card_batt = QVBoxLayout(self.card_batt)
        self.vl_card_batt.setObjectName(u"vl_card_batt")
        self.lbl_batt_title = QLabel(self.card_batt)
        self.lbl_batt_title.setObjectName(u"lbl_batt_title")
        self.lbl_batt_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vl_card_batt.addWidget(self.lbl_batt_title)

        self.lbl_batt_value = QLabel(self.card_batt)
        self.lbl_batt_value.setObjectName(u"lbl_batt_value")
        self.lbl_batt_value.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vl_card_batt.addWidget(self.lbl_batt_value)

        self.lbl_batt_unit = QLabel(self.card_batt)
        self.lbl_batt_unit.setObjectName(u"lbl_batt_unit")
        self.lbl_batt_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vl_card_batt.addWidget(self.lbl_batt_unit)


        self.grid_cards_2x2.addWidget(self.card_batt, 0, 0, 1, 1)

        self.card_temp = QFrame(OverviewForm)
        self.card_temp.setObjectName(u"card_temp")
        sizePolicy.setHeightForWidth(self.card_temp.sizePolicy().hasHeightForWidth())
        self.card_temp.setSizePolicy(sizePolicy)
        self.vl_card_temp = QVBoxLayout(self.card_temp)
        self.vl_card_temp.setObjectName(u"vl_card_temp")
        self.lbl_temp_title = QLabel(self.card_temp)
        self.lbl_temp_title.setObjectName(u"lbl_temp_title")
        self.lbl_temp_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vl_card_temp.addWidget(self.lbl_temp_title)

        self.lbl_temp_value = QLabel(self.card_temp)
        self.lbl_temp_value.setObjectName(u"lbl_temp_value")
        self.lbl_temp_value.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vl_card_temp.addWidget(self.lbl_temp_value)

        self.lbl_temp_unit = QLabel(self.card_temp)
        self.lbl_temp_unit.setObjectName(u"lbl_temp_unit")
        self.lbl_temp_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vl_card_temp.addWidget(self.lbl_temp_unit)


        self.grid_cards_2x2.addWidget(self.card_temp, 0, 1, 1, 1)

        self.card_task_amt = QFrame(OverviewForm)
        self.card_task_amt.setObjectName(u"card_task_amt")
        sizePolicy.setHeightForWidth(self.card_task_amt.sizePolicy().hasHeightForWidth())
        self.card_task_amt.setSizePolicy(sizePolicy)
        self.vl_card_task_amt = QVBoxLayout(self.card_task_amt)
        self.vl_card_task_amt.setObjectName(u"vl_card_task_amt")
        self.lbl_task_title = QLabel(self.card_task_amt)
        self.lbl_task_title.setObjectName(u"lbl_task_title")
        self.lbl_task_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vl_card_task_amt.addWidget(self.lbl_task_title)

        self.lbl_task_value = QLabel(self.card_task_amt)
        self.lbl_task_value.setObjectName(u"lbl_task_value")
        self.lbl_task_value.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vl_card_task_amt.addWidget(self.lbl_task_value)

        self.lbl_task_unit = QLabel(self.card_task_amt)
        self.lbl_task_unit.setObjectName(u"lbl_task_unit")
        self.lbl_task_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vl_card_task_amt.addWidget(self.lbl_task_unit)


        self.grid_cards_2x2.addWidget(self.card_task_amt, 1, 0, 1, 1)

        self.card_take_time = QFrame(OverviewForm)
        self.card_take_time.setObjectName(u"card_take_time")
        sizePolicy.setHeightForWidth(self.card_take_time.sizePolicy().hasHeightForWidth())
        self.card_take_time.setSizePolicy(sizePolicy)
        self.vl_card_take_time = QVBoxLayout(self.card_take_time)
        self.vl_card_take_time.setObjectName(u"vl_card_take_time")
        self.lbl_time_title = QLabel(self.card_take_time)
        self.lbl_time_title.setObjectName(u"lbl_time_title")
        self.lbl_time_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vl_card_take_time.addWidget(self.lbl_time_title)

        self.lbl_time_value = QLabel(self.card_take_time)
        self.lbl_time_value.setObjectName(u"lbl_time_value")
        self.lbl_time_value.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vl_card_take_time.addWidget(self.lbl_time_value)

        self.lbl_time_unit = QLabel(self.card_take_time)
        self.lbl_time_unit.setObjectName(u"lbl_time_unit")
        self.lbl_time_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vl_card_take_time.addWidget(self.lbl_time_unit)


        self.grid_cards_2x2.addWidget(self.card_take_time, 1, 1, 1, 1)


        self.vl_root.addLayout(self.grid_cards_2x2)


        self.retranslateUi(OverviewForm)

        QMetaObject.connectSlotsByName(OverviewForm)
    # setupUi

    def retranslateUi(self, OverviewForm):
        self.lbl_robot_id.setText(QCoreApplication.translate("OverviewForm", u"ROBOT: agv1", None))
        self.lbl_batt_title.setText(QCoreApplication.translate("OverviewForm", u"BATTERY", None))
        self.lbl_batt_value.setText(QCoreApplication.translate("OverviewForm", u"0", None))
        self.lbl_batt_unit.setText(QCoreApplication.translate("OverviewForm", u"%", None))
        self.lbl_temp_title.setText(QCoreApplication.translate("OverviewForm", u"TEMP", None))
        self.lbl_temp_value.setText(QCoreApplication.translate("OverviewForm", u"0.0", None))
        self.lbl_temp_unit.setText(QCoreApplication.translate("OverviewForm", u"\u00b0C", None))
        self.lbl_task_title.setText(QCoreApplication.translate("OverviewForm", u"AMOUNT OF TASK", None))
        self.lbl_task_value.setText(QCoreApplication.translate("OverviewForm", u"0", None))
        self.lbl_task_unit.setText(QCoreApplication.translate("OverviewForm", u"tasks", None))
        self.lbl_time_title.setText(QCoreApplication.translate("OverviewForm", u"TOTAL TAKE TIME", None))
        self.lbl_time_value.setText(QCoreApplication.translate("OverviewForm", u"0", None))
        self.lbl_time_unit.setText(QCoreApplication.translate("OverviewForm", u"sec", None))
        pass
    # retranslateUi

