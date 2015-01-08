# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fileTransfer.ui'
#
# Created: Tue Dec 16 15:46:23 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_FileTransfers(object):
    def setupUi(self, FileTransfers):
        FileTransfers.setObjectName("FileTransfers")
        FileTransfers.resize(530, 320)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/quip/Images/quip-bubble.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        FileTransfers.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(FileTransfers)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.transferTableWidget = QtGui.QTableWidget(self.centralwidget)
        self.transferTableWidget.setFocusPolicy(QtCore.Qt.TabFocus)
        self.transferTableWidget.setFrameShadow(QtGui.QFrame.Plain)
        self.transferTableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.transferTableWidget.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.transferTableWidget.setShowGrid(False)
        self.transferTableWidget.setObjectName("transferTableWidget")
        self.transferTableWidget.setColumnCount(5)
        self.transferTableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.transferTableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.transferTableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.transferTableWidget.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.transferTableWidget.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.transferTableWidget.setHorizontalHeaderItem(4, item)
        self.transferTableWidget.horizontalHeader().setVisible(False)
        self.transferTableWidget.horizontalHeader().setCascadingSectionResizes(True)
        self.transferTableWidget.horizontalHeader().setStretchLastSection(False)
        self.transferTableWidget.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.transferTableWidget)
        FileTransfers.setCentralWidget(self.centralwidget)

        self.retranslateUi(FileTransfers)
        QtCore.QMetaObject.connectSlotsByName(FileTransfers)

    def retranslateUi(self, FileTransfers):
        FileTransfers.setWindowTitle(QtGui.QApplication.translate("FileTransfers", "File Transfers", None, QtGui.QApplication.UnicodeUTF8))
        self.transferTableWidget.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("FileTransfers", "Friend", None, QtGui.QApplication.UnicodeUTF8))
        self.transferTableWidget.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("FileTransfers", "File Details", None, QtGui.QApplication.UnicodeUTF8))
        self.transferTableWidget.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("FileTransfers", "Progress", None, QtGui.QApplication.UnicodeUTF8))

from . import quip_qt_rc
