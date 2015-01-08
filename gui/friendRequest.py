# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'friendRequest.ui'
#
# Created: Tue Dec 16 15:46:23 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_FriendRequest(object):
    def setupUi(self, FriendRequest):
        FriendRequest.setObjectName("FriendRequest")
        FriendRequest.resize(640, 200)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/quip/Images/quip-bubble.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        FriendRequest.setWindowIcon(icon)
        FriendRequest.setStyleSheet("background-color: white;")
        self.horizontalLayout = QtGui.QHBoxLayout(FriendRequest)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.avatarVBoxLayout = QtGui.QVBoxLayout()
        self.avatarVBoxLayout.setObjectName("avatarVBoxLayout")
        self.avatarLabel = QtGui.QLabel(FriendRequest)
        self.avatarLabel.setText("")
        self.avatarLabel.setPixmap(QtGui.QPixmap(":/quip/Images/default-avatar-64x64.png"))
        self.avatarLabel.setObjectName("avatarLabel")
        self.avatarVBoxLayout.addWidget(self.avatarLabel)
        self.profileButton = QtGui.QPushButton(FriendRequest)
        self.profileButton.setMaximumSize(QtCore.QSize(100, 100))
        self.profileButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.profileButton.setStyleSheet("border-style: none;")
        self.profileButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/quip/Images/dialog-information.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.profileButton.setIcon(icon1)
        self.profileButton.setFlat(True)
        self.profileButton.setObjectName("profileButton")
        self.avatarVBoxLayout.addWidget(self.profileButton)
        self.statusLabel = QtGui.QLabel(FriendRequest)
        self.statusLabel.setStyleSheet("color: red;")
        self.statusLabel.setObjectName("statusLabel")
        self.avatarVBoxLayout.addWidget(self.statusLabel)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.avatarVBoxLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.avatarVBoxLayout)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.aliasHBoxLayout = QtGui.QHBoxLayout()
        self.aliasHBoxLayout.setObjectName("aliasHBoxLayout")
        self.aliasLabel = QtGui.QLabel(FriendRequest)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.aliasLabel.setFont(font)
        self.aliasLabel.setObjectName("aliasLabel")
        self.aliasHBoxLayout.addWidget(self.aliasLabel)
        self.nextButton = QtGui.QPushButton(FriendRequest)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nextButton.sizePolicy().hasHeightForWidth())
        self.nextButton.setSizePolicy(sizePolicy)
        self.nextButton.setMaximumSize(QtCore.QSize(40, 16777215))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.nextButton.setFont(font)
        self.nextButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.nextButton.setObjectName("nextButton")
        self.aliasHBoxLayout.addWidget(self.nextButton)
        self.verticalLayout.addLayout(self.aliasHBoxLayout)
        self.messagePlainTextEdit = QtGui.QPlainTextEdit(FriendRequest)
        self.messagePlainTextEdit.setMaximumSize(QtCore.QSize(16777215, 80))
        self.messagePlainTextEdit.setStyleSheet("border-style: dotted;\n"
"border-width: 1px;\n"
"border-color: black;")
        self.messagePlainTextEdit.setReadOnly(True)
        self.messagePlainTextEdit.setObjectName("messagePlainTextEdit")
        self.verticalLayout.addWidget(self.messagePlainTextEdit)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.progressHBoxLayout = QtGui.QHBoxLayout()
        self.progressHBoxLayout.setObjectName("progressHBoxLayout")
        self.progressBar = QtGui.QProgressBar(FriendRequest)
        self.progressBar.setMaximumSize(QtCore.QSize(512, 15))
        self.progressBar.setMaximum(0)
        self.progressBar.setProperty("value", -1)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setObjectName("progressBar")
        self.progressHBoxLayout.addWidget(self.progressBar)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.progressHBoxLayout.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.progressHBoxLayout)
        self.buttonHBoxLayout = QtGui.QHBoxLayout()
        self.buttonHBoxLayout.setSpacing(30)
        self.buttonHBoxLayout.setObjectName("buttonHBoxLayout")
        self.acceptButton = QtGui.QPushButton(FriendRequest)
        font = QtGui.QFont()
        font.setWeight(50)
        font.setBold(False)
        self.acceptButton.setFont(font)
        self.acceptButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.acceptButton.setStyleSheet("border-color: rgba(140, 217, 140, 100);\n"
"border-width: 1px;\n"
"border-style: solid;\n"
"border-radius: 10px;\n"
"background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 white, stop: 1 rgba(140, 217, 140, 100));")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/quip/Images/tick.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.acceptButton.setIcon(icon2)
        self.acceptButton.setObjectName("acceptButton")
        self.buttonHBoxLayout.addWidget(self.acceptButton)
        self.ignoreButton = QtGui.QPushButton(FriendRequest)
        self.ignoreButton.setStyleSheet("border-color: rgba(185, 216, 234, 100);\n"
"border-width: 1px;\n"
"border-style: solid;\n"
"border-radius: 10px;\n"
"background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 white, stop: 1 rgba(185, 216, 234, 100));")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/quip/Images/remove-32x32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ignoreButton.setIcon(icon3)
        self.ignoreButton.setObjectName("ignoreButton")
        self.buttonHBoxLayout.addWidget(self.ignoreButton)
        self.blockButton = QtGui.QPushButton(FriendRequest)
        self.blockButton.setStyleSheet("border-color: rgba(225, 33, 33, 100);\n"
"border-width: 1px;\n"
"border-style: solid;\n"
"border-radius: 10px;\n"
"background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 white, stop: 1 rgba(225, 33, 33, 100));")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/quip/Images/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.blockButton.setIcon(icon4)
        self.blockButton.setObjectName("blockButton")
        self.buttonHBoxLayout.addWidget(self.blockButton)
        self.verticalLayout.addLayout(self.buttonHBoxLayout)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(FriendRequest)
        QtCore.QMetaObject.connectSlotsByName(FriendRequest)

    def retranslateUi(self, FriendRequest):
        FriendRequest.setWindowTitle(QtGui.QApplication.translate("FriendRequest", "Friend Request", None, QtGui.QApplication.UnicodeUTF8))
        self.statusLabel.setText(QtGui.QApplication.translate("FriendRequest", "Offline", None, QtGui.QApplication.UnicodeUTF8))
        self.aliasLabel.setText(QtGui.QApplication.translate("FriendRequest", "User Alias (User ID)", None, QtGui.QApplication.UnicodeUTF8))
        self.nextButton.setText(QtGui.QApplication.translate("FriendRequest", ">>", None, QtGui.QApplication.UnicodeUTF8))
        self.acceptButton.setText(QtGui.QApplication.translate("FriendRequest", "Accept", None, QtGui.QApplication.UnicodeUTF8))
        self.ignoreButton.setText(QtGui.QApplication.translate("FriendRequest", "Ignore", None, QtGui.QApplication.UnicodeUTF8))
        self.blockButton.setText(QtGui.QApplication.translate("FriendRequest", "Block", None, QtGui.QApplication.UnicodeUTF8))

from . import quip_qt_rc
