# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analytics.ui'
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
from PySide6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_AnalyticsForm(object):
    def setupUi(self, AnalyticsForm):
        if not AnalyticsForm.objectName():
            AnalyticsForm.setObjectName(u"AnalyticsForm")
        AnalyticsForm.resize(1000, 650)
        self.vl_root = QVBoxLayout(AnalyticsForm)
        self.vl_root.setSpacing(20)
        self.vl_root.setObjectName(u"vl_root")
        self.vl_root.setContentsMargins(20, 20, 20, 20)
        self.hl_kpi_container = QHBoxLayout()
        self.hl_kpi_container.setSpacing(10)
        self.hl_kpi_container.setObjectName(u"hl_kpi_container")

        self.vl_root.addLayout(self.hl_kpi_container)

        self.gb_dest = QGroupBox(AnalyticsForm)
        self.gb_dest.setObjectName(u"gb_dest")
        self.vl_dest_container = QVBoxLayout(self.gb_dest)
        self.vl_dest_container.setSpacing(0)
        self.vl_dest_container.setObjectName(u"vl_dest_container")
        self.vl_dest_container.setContentsMargins(10, 10, 10, 10)

        self.vl_root.addWidget(self.gb_dest)


        self.retranslateUi(AnalyticsForm)

        QMetaObject.connectSlotsByName(AnalyticsForm)
    # setupUi

    def retranslateUi(self, AnalyticsForm):
        self.gb_dest.setTitle(QCoreApplication.translate("AnalyticsForm", u"Top Destinations Statistics (target_area)", None))
        pass
    # retranslateUi

