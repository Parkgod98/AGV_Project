# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QStackedWidget, QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(892, 480)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.vl_root = QVBoxLayout(self.centralwidget)
        self.vl_root.setObjectName(u"vl_root")
        self.frame_nav = QFrame(self.centralwidget)
        self.frame_nav.setObjectName(u"frame_nav")
        self.frame_nav.setMinimumSize(QSize(0, 60))
        self.frame_nav.setFrameShape(QFrame.Shape.StyledPanel)
        self.hl_nav = QHBoxLayout(self.frame_nav)
        self.hl_nav.setSpacing(8)
        self.hl_nav.setObjectName(u"hl_nav")
        self.btn_overview = QPushButton(self.frame_nav)
        self.btn_overview.setObjectName(u"btn_overview")
        self.btn_overview.setMinimumSize(QSize(110, 44))

        self.hl_nav.addWidget(self.btn_overview)

        self.btn_control = QPushButton(self.frame_nav)
        self.btn_control.setObjectName(u"btn_control")
        self.btn_control.setMinimumSize(QSize(110, 44))

        self.hl_nav.addWidget(self.btn_control)

        self.btn_analytics = QPushButton(self.frame_nav)
        self.btn_analytics.setObjectName(u"btn_analytics")
        self.btn_analytics.setMinimumSize(QSize(130, 44))

        self.hl_nav.addWidget(self.btn_analytics)

        self.btn_map = QPushButton(self.frame_nav)
        self.btn_map.setObjectName(u"btn_map")
        self.btn_map.setMinimumSize(QSize(90, 44))

        self.hl_nav.addWidget(self.btn_map)

        self.btn_tasks = QPushButton(self.frame_nav)
        self.btn_tasks.setObjectName(u"btn_tasks")
        self.btn_tasks.setMinimumSize(QSize(90, 44))

        self.hl_nav.addWidget(self.btn_tasks)

        self.btn_logs = QPushButton(self.frame_nav)
        self.btn_logs.setObjectName(u"btn_logs")
        self.btn_logs.setMinimumSize(QSize(80, 44))

        self.hl_nav.addWidget(self.btn_logs)

        self.spacer_nav = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hl_nav.addItem(self.spacer_nav)

        self.lbl_top_status = QLabel(self.frame_nav)
        self.lbl_top_status.setObjectName(u"lbl_top_status")
        self.lbl_top_status.setMinimumSize(QSize(180, 0))

        self.hl_nav.addWidget(self.lbl_top_status)


        self.vl_root.addWidget(self.frame_nav)

        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page_overview = QWidget()
        self.page_overview.setObjectName(u"page_overview")
        self.stackedWidget.addWidget(self.page_overview)
        self.page_control = QWidget()
        self.page_control.setObjectName(u"page_control")
        self.stackedWidget.addWidget(self.page_control)
        self.page_analytics = QWidget()
        self.page_analytics.setObjectName(u"page_analytics")
        self.stackedWidget.addWidget(self.page_analytics)
        self.page_map = QWidget()
        self.page_map.setObjectName(u"page_map")
        self.stackedWidget.addWidget(self.page_map)
        self.page_tasks = QWidget()
        self.page_tasks.setObjectName(u"page_tasks")
        self.stackedWidget.addWidget(self.page_tasks)
        self.page_logs = QWidget()
        self.page_logs.setObjectName(u"page_logs")
        self.stackedWidget.addWidget(self.page_logs)

        self.vl_root.addWidget(self.stackedWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setVisible(True)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"AGV HMI", None))
        self.btn_overview.setText(QCoreApplication.translate("MainWindow", u"OVERVIEW", None))
        self.btn_control.setText(QCoreApplication.translate("MainWindow", u"CONTROL", None))
        self.btn_analytics.setText(QCoreApplication.translate("MainWindow", u"ANALYTICS", None))
        self.btn_map.setText(QCoreApplication.translate("MainWindow", u"MAP", None))
        self.btn_tasks.setText(QCoreApplication.translate("MainWindow", u"TASKS", None))
        self.btn_logs.setText(QCoreApplication.translate("MainWindow", u"LOGS", None))
        self.lbl_top_status.setText(QCoreApplication.translate("MainWindow", u"MQTT: - | FS: -", None))
    # retranslateUi

