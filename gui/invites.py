# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'invites.ui'
#
# Created: Sun Apr 19 15:24:51 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Invites(object):
    def setupUi(self, Invites):
        Invites.setObjectName("Invites")
        Invites.resize(640, 480)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/quip/Images/quip-bubble.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Invites.setWindowIcon(icon)
        Invites.setStyleSheet("background-color: white;")
        self.centralwidget = QtGui.QWidget(Invites)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.clearHBoxLayout = QtGui.QHBoxLayout()
        self.clearHBoxLayout.setObjectName("clearHBoxLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.clearHBoxLayout.addItem(spacerItem)
        self.clearButton = QtGui.QPushButton(self.centralwidget)
        self.clearButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.clearButton.setStyleSheet("background-color: rgba(255, 0, 0, 100);\n"
"")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/quip/Images/remove-32x32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.clearButton.setIcon(icon1)
        self.clearButton.setObjectName("clearButton")
        self.clearHBoxLayout.addWidget(self.clearButton)
        self.gridLayout.addLayout(self.clearHBoxLayout, 2, 0, 1, 1)
        self.generateHBoxLayout = QtGui.QHBoxLayout()
        self.generateHBoxLayout.setContentsMargins(-1, -1, -1, 15)
        self.generateHBoxLayout.setObjectName("generateHBoxLayout")
        self.availableLabel = QtGui.QLabel(self.centralwidget)
        self.availableLabel.setObjectName("availableLabel")
        self.generateHBoxLayout.addWidget(self.availableLabel)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.generateHBoxLayout.addItem(spacerItem1)
        self.generateButton = QtGui.QPushButton(self.centralwidget)
        self.generateButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.generateButton.setStyleSheet("background-color: rgba(140, 217, 140, 100);")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/quip/Images/invite-add-32x32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.generateButton.setIcon(icon2)
        self.generateButton.setFlat(False)
        self.generateButton.setObjectName("generateButton")
        self.generateHBoxLayout.addWidget(self.generateButton)
        self.gridLayout.addLayout(self.generateHBoxLayout, 0, 0, 1, 1)
        self.invitesListView = QtGui.QListView(self.centralwidget)
        self.invitesListView.setObjectName("invitesListView")
        self.gridLayout.addWidget(self.invitesListView, 1, 0, 1, 1)
        self.invitesDescription = QtGui.QTextEdit(self.centralwidget)
        self.invitesDescription.setStyleSheet("border-top: 1px dotted black;")
        self.invitesDescription.setFrameShadow(QtGui.QFrame.Plain)
        self.invitesDescription.setReadOnly(True)
        self.invitesDescription.setObjectName("invitesDescription")
        self.gridLayout.addWidget(self.invitesDescription, 3, 0, 1, 1)
        Invites.setCentralWidget(self.centralwidget)

        self.retranslateUi(Invites)
        QtCore.QMetaObject.connectSlotsByName(Invites)

    def retranslateUi(self, Invites):
        Invites.setWindowTitle(QtGui.QApplication.translate("Invites", "Invites", None, QtGui.QApplication.UnicodeUTF8))
        self.clearButton.setToolTip(QtGui.QApplication.translate("Invites", "Clear claimed and expired invites", None, QtGui.QApplication.UnicodeUTF8))
        self.clearButton.setText(QtGui.QApplication.translate("Invites", "Clear Invites", None, QtGui.QApplication.UnicodeUTF8))
        self.availableLabel.setText(QtGui.QApplication.translate("Invites", "Invites Available: 0", None, QtGui.QApplication.UnicodeUTF8))
        self.generateButton.setText(QtGui.QApplication.translate("Invites", "Generate Invite", None, QtGui.QApplication.UnicodeUTF8))
        self.invitesDescription.setHtml(QtGui.QApplication.translate("Invites", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Droid Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Invite codes can be used in Account Creation to bypass free account limits, and to provide extra features to a new account for a limited time.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">         <img src=\":/quip/Images/invite_unclaimed-16x16.png\" />     Invite code is unclaimed</p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">            <img src=\":/quip/Images/invite_claimed-16x16.png\" />     Invite code has been used</p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/quip/Images/invite_expired-16x16.png\" />     Invite code expired</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

from . import quip_qt_rc
