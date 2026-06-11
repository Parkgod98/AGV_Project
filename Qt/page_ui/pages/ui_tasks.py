# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tasks.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHeaderView, QSizePolicy,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)
class Ui_TasksForm(object):
    def setupUi(self, TasksForm):
        if not TasksForm.objectName():
            TasksForm.setObjectName(u"TasksForm")
        TasksForm.resize(1100, 750)
        self.vl_root = QVBoxLayout(TasksForm)
        self.vl_root.setSpacing(10)
        self.vl_root.setObjectName(u"vl_root")
        self.vl_root.setContentsMargins(15, 15, 15, 15)
        self.table = QTableWidget(TasksForm)
        if (self.table.columnCount() < 4):
            self.table.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.table.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.table.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.table.setObjectName(u"table")
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.vl_root.addWidget(self.table)


        self.retranslateUi(TasksForm)

        QMetaObject.connectSlotsByName(TasksForm)
    # setupUi

    def retranslateUi(self, TasksForm):
        ___qtablewidgetitem = self.table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("TasksForm", u"Created At", None));
        ___qtablewidgetitem1 = self.table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("TasksForm", u"Task ID", None));
        ___qtablewidgetitem2 = self.table.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("TasksForm", u"Type", None));
        ___qtablewidgetitem3 = self.table.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("TasksForm", u"Status", None));
        pass
    # retranslateUi

