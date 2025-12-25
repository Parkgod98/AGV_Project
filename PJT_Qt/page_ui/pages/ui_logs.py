# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'logs.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_LogsForm(object):
    def setupUi(self, LogsForm):
        if not LogsForm.objectName():
            LogsForm.setObjectName(u"LogsForm")
        LogsForm.resize(1000, 700)
        self.vl_root = QVBoxLayout(LogsForm)
        self.vl_root.setSpacing(10)
        self.vl_root.setObjectName(u"vl_root")
        self.vl_root.setContentsMargins(15, 15, 15, 15)
        self.hl_top = QHBoxLayout()
        self.hl_top.setObjectName(u"hl_top")
        self.lbl_title = QLabel(LogsForm)
        self.lbl_title.setObjectName(u"lbl_title")
        self.lbl_title.setStyleSheet(u"font-weight: bold; color: #3b82f6; font-size: 14px;")

        self.hl_top.addWidget(self.lbl_title)

        self.sp = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hl_top.addItem(self.sp)

        self.btn_clear = QPushButton(LogsForm)
        self.btn_clear.setObjectName(u"btn_clear")
        self.btn_clear.setMinimumWidth(100)

        self.hl_top.addWidget(self.btn_clear)


        self.vl_root.addLayout(self.hl_top)

        self.text = QTextEdit(LogsForm)
        self.text.setObjectName(u"text")
        self.text.setReadOnly(True)

        self.vl_root.addWidget(self.text)


        self.retranslateUi(LogsForm)

        QMetaObject.connectSlotsByName(LogsForm)
    # setupUi

    def retranslateUi(self, LogsForm):
        self.lbl_title.setText(QCoreApplication.translate("LogsForm", u"SYSTEM LOGS", None))
        self.btn_clear.setText(QCoreApplication.translate("LogsForm", u"Clear All", None))
        self.text.setPlaceholderText(QCoreApplication.translate("LogsForm", u"Waiting for logs...", None))
        pass
    # retranslateUi

