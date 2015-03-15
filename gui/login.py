# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created: Mon Mar  9 11:21:34 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Login(object):
    def setupUi(self, Login):
        Login.setObjectName("Login")
        Login.resize(320, 240)
        Login.setMaximumSize(QtCore.QSize(320, 240))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/quip/Images/quip-bubble.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Login.setWindowIcon(icon)
        Login.setAutoFillBackground(False)
        Login.setStyleSheet("background-color:white")
        self.logoLabel = QtGui.QLabel(Login)
        self.logoLabel.setGeometry(QtCore.QRect(102, 10, 101, 91))
        self.logoLabel.setText("")
        self.logoLabel.setPixmap(QtGui.QPixmap(":/quip/Images/quip-bubble.png"))
        self.logoLabel.setScaledContents(True)
        self.logoLabel.setObjectName("logoLabel")
        self.layoutWidget = QtGui.QWidget(Login)
        self.layoutWidget.setGeometry(QtCore.QRect(50, 110, 211, 100))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setSpacing(9)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.profileComboBox = QtGui.QComboBox(self.layoutWidget)
        self.profileComboBox.setStyleSheet("border-color: rgba(140, 217, 140, 100);\n"
"border-width: 1px;\n"
"border-radius: 5px;\n"
"border-style: solid;\n"
"color: black;\n"
"")
        self.profileComboBox.setIconSize(QtCore.QSize(16, 16))
        self.profileComboBox.setFrame(False)
        self.profileComboBox.setObjectName("profileComboBox")
        self.profileComboBox.addItem("")
        self.verticalLayout.addWidget(self.profileComboBox)
        self.phraseInput = QtGui.QLineEdit(self.layoutWidget)
        self.phraseInput.setStyleSheet("border-color: grey;\n"
"border-width: 1px;\n"
"border-radius: 5px;\n"
"border-style: solid;")
        self.phraseInput.setInputMask("")
        self.phraseInput.setText("")
        self.phraseInput.setEchoMode(QtGui.QLineEdit.Password)
        self.phraseInput.setReadOnly(False)
        self.phraseInput.setObjectName("phraseInput")
        self.verticalLayout.addWidget(self.phraseInput)
        self.progressBar = QtGui.QProgressBar(self.layoutWidget)
        self.progressBar.setMaximumSize(QtCore.QSize(16777215, 20))
        self.progressBar.setMaximum(0)
        self.progressBar.setProperty("value", -1)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.layoutWidget1 = QtGui.QWidget(Login)
        self.layoutWidget1.setGeometry(QtCore.QRect(10, 200, 301, 35))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.horizontalLayout = QtGui.QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.newAccountButton = QtGui.QPushButton(self.layoutWidget1)
        self.newAccountButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.newAccountButton.setStyleSheet("background-color: rgba(185, 216, 234, 100)")
        self.newAccountButton.setAutoDefault(False)
        self.newAccountButton.setObjectName("newAccountButton")
        self.horizontalLayout.addWidget(self.newAccountButton)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.loginButton = QtGui.QPushButton(self.layoutWidget1)
        self.loginButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.loginButton.setStyleSheet("background-color: rgba(140, 217, 140, 100);")
        self.loginButton.setAutoDefault(False)
        self.loginButton.setDefault(False)
        self.loginButton.setObjectName("loginButton")
        self.horizontalLayout.addWidget(self.loginButton)
        self.failedLoginLabel = QtGui.QLabel(Login)
        self.failedLoginLabel.setEnabled(True)
        self.failedLoginLabel.setGeometry(QtCore.QRect(30, 180, 251, 20))
        self.failedLoginLabel.setStyleSheet("color: red;")
        self.failedLoginLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.failedLoginLabel.setObjectName("failedLoginLabel")
        self.recoveryButton = QtGui.QPushButton(Login)
        self.recoveryButton.setGeometry(QtCore.QRect(270, 130, 32, 32))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.recoveryButton.sizePolicy().hasHeightForWidth())
        self.recoveryButton.setSizePolicy(sizePolicy)
        self.recoveryButton.setStyleSheet("border: none;")
        self.recoveryButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/quip/Images/recover-unlock-32x32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.recoveryButton.setIcon(icon1)
        self.recoveryButton.setIconSize(QtCore.QSize(32, 32))
        self.recoveryButton.setFlat(True)
        self.recoveryButton.setObjectName("recoveryButton")

        self.retranslateUi(Login)
        self.profileComboBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Login)

    def retranslateUi(self, Login):
        Login.setWindowTitle(QtGui.QApplication.translate("Login", "Login", None, QtGui.QApplication.UnicodeUTF8))
        self.profileComboBox.setItemText(0, QtGui.QApplication.translate("Login", "Select Profile...", None, QtGui.QApplication.UnicodeUTF8))
        self.phraseInput.setToolTip(QtGui.QApplication.translate("Login", "Enter profile passphrase", None, QtGui.QApplication.UnicodeUTF8))
        self.phraseInput.setPlaceholderText(QtGui.QApplication.translate("Login", "Passphrase", None, QtGui.QApplication.UnicodeUTF8))
        self.newAccountButton.setText(QtGui.QApplication.translate("Login", "New Account", None, QtGui.QApplication.UnicodeUTF8))
        self.loginButton.setText(QtGui.QApplication.translate("Login", "Login", None, QtGui.QApplication.UnicodeUTF8))
        self.failedLoginLabel.setText(QtGui.QApplication.translate("Login", "Login Failed", None, QtGui.QApplication.UnicodeUTF8))
        self.recoveryButton.setToolTip(QtGui.QApplication.translate("Login", "Recover Account", None, QtGui.QApplication.UnicodeUTF8))

from . import quip_qt_rc
