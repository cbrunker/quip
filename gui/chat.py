# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'chat.ui'
#
# Created: Tue Dec 16 15:46:23 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Chat(object):
    def setupUi(self, Chat):
        Chat.setObjectName("Chat")
        Chat.resize(640, 480)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/quip/Images/quip-bubble.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Chat.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(Chat)
        self.centralwidget.setStyleSheet("background-color: white;")
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(2, 2, 2, 2)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.friendWidget = QtGui.QWidget(self.centralwidget)
        self.friendWidget.setMaximumSize(QtCore.QSize(16777215, 100))
        self.friendWidget.setStyleSheet("background-color: white;")
        self.friendWidget.setObjectName("friendWidget")
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.friendWidget)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.friendAvatarLabel = QtGui.QLabel(self.friendWidget)
        self.friendAvatarLabel.setAutoFillBackground(False)
        self.friendAvatarLabel.setStyleSheet("border-width: 3px;\n"
"border-style: groove;\n"
"border-color: rgba(255, 255, 255, 255);\n"
"background-color: rgba(255, 255, 255, 255);")
        self.friendAvatarLabel.setText("")
        self.friendAvatarLabel.setPixmap(QtGui.QPixmap(":/quip/Images/default-avatar-64x64.png"))
        self.friendAvatarLabel.setObjectName("friendAvatarLabel")
        self.horizontalLayout_5.addWidget(self.friendAvatarLabel)
        self.friendHBoxLayout = QtGui.QHBoxLayout()
        self.friendHBoxLayout.setSpacing(4)
        self.friendHBoxLayout.setObjectName("friendHBoxLayout")
        self.friendVBoxLayout = QtGui.QVBoxLayout()
        self.friendVBoxLayout.setSpacing(0)
        self.friendVBoxLayout.setContentsMargins(-1, 0, -1, -1)
        self.friendVBoxLayout.setObjectName("friendVBoxLayout")
        self.label = QtGui.QLabel(self.friendWidget)
        self.label.setMaximumSize(QtCore.QSize(16777215, 10))
        self.label.setStyleSheet("background-color: white;")
        self.label.setText("")
        self.label.setObjectName("label")
        self.friendVBoxLayout.addWidget(self.label)
        self.friendAliasLineEdit = QtGui.QLineEdit(self.friendWidget)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.friendAliasLineEdit.setFont(font)
        self.friendAliasLineEdit.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.friendAliasLineEdit.setStyleSheet("")
        self.friendAliasLineEdit.setText("")
        self.friendAliasLineEdit.setMaxLength(36)
        self.friendAliasLineEdit.setFrame(False)
        self.friendAliasLineEdit.setReadOnly(True)
        self.friendAliasLineEdit.setObjectName("friendAliasLineEdit")
        self.friendVBoxLayout.addWidget(self.friendAliasLineEdit)
        self.friendCommentTextEdit = QtGui.QTextEdit(self.friendWidget)
        self.friendCommentTextEdit.setFrameShadow(QtGui.QFrame.Plain)
        self.friendCommentTextEdit.setReadOnly(True)
        self.friendCommentTextEdit.setObjectName("friendCommentTextEdit")
        self.friendVBoxLayout.addWidget(self.friendCommentTextEdit)
        self.friendHBoxLayout.addLayout(self.friendVBoxLayout)
        self.horizontalLayout_5.addLayout(self.friendHBoxLayout)
        self.verticalLayout.addWidget(self.friendWidget)
        self.historyTextBrowser = QtGui.QTextBrowser(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(self.historyTextBrowser.sizePolicy().hasHeightForWidth())
        self.historyTextBrowser.setSizePolicy(sizePolicy)
        self.historyTextBrowser.setStyleSheet("border-width: 1px;\n"
"border-radius: 5px;\n"
"border-style: dashed;\n"
"border-color: rgba(213, 213, 213, 150);\n"
"background-color: rgb(252, 252, 252)")
        self.historyTextBrowser.setFrameShadow(QtGui.QFrame.Plain)
        self.historyTextBrowser.setUndoRedoEnabled(False)
        self.historyTextBrowser.setReadOnly(True)
        self.historyTextBrowser.setOpenExternalLinks(True)
        self.historyTextBrowser.setObjectName("historyTextBrowser")
        self.verticalLayout.addWidget(self.historyTextBrowser)
        self.chatWidget = QtGui.QWidget(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.chatWidget.sizePolicy().hasHeightForWidth())
        self.chatWidget.setSizePolicy(sizePolicy)
        self.chatWidget.setAutoFillBackground(False)
        self.chatWidget.setStyleSheet("")
        self.chatWidget.setObjectName("chatWidget")
        self.gridLayout_2 = QtGui.QGridLayout(self.chatWidget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.chatHBoxLayout = QtGui.QHBoxLayout()
        self.chatHBoxLayout.setObjectName("chatHBoxLayout")
        self.chatVBoxLayout = QtGui.QVBoxLayout()
        self.chatVBoxLayout.setObjectName("chatVBoxLayout")
        self.chatToolbar = QtGui.QWidget(self.chatWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chatToolbar.sizePolicy().hasHeightForWidth())
        self.chatToolbar.setSizePolicy(sizePolicy)
        self.chatToolbar.setStyleSheet("background-color: rgba(217, 217, 217, 100);\n"
"border-width: 1px;\n"
"border-style: solid;\n"
"border-radius: 10px;")
        self.chatToolbar.setObjectName("chatToolbar")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.chatToolbar)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.emoteToolButton = QtGui.QToolButton(self.chatToolbar)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/quip/Images/emoticons/smile.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.emoteToolButton.setIcon(icon1)
        self.emoteToolButton.setAutoRaise(True)
        self.emoteToolButton.setObjectName("emoteToolButton")
        self.horizontalLayout_2.addWidget(self.emoteToolButton)
        self.transferToolButton = QtGui.QToolButton(self.chatToolbar)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/quip/Images/attachment-32x32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.transferToolButton.setIcon(icon2)
        self.transferToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.transferToolButton.setAutoRaise(True)
        self.transferToolButton.setObjectName("transferToolButton")
        self.horizontalLayout_2.addWidget(self.transferToolButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.chatVBoxLayout.addWidget(self.chatToolbar)
        self.chatTextEdit = QtGui.QTextEdit(self.chatWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chatTextEdit.sizePolicy().hasHeightForWidth())
        self.chatTextEdit.setSizePolicy(sizePolicy)
        self.chatTextEdit.setStyleSheet("")
        self.chatTextEdit.setFrameShape(QtGui.QFrame.Panel)
        self.chatTextEdit.setFrameShadow(QtGui.QFrame.Raised)
        self.chatTextEdit.setLineWidth(2)
        self.chatTextEdit.setMidLineWidth(2)
        self.chatTextEdit.setObjectName("chatTextEdit")
        self.chatVBoxLayout.addWidget(self.chatTextEdit)
        self.chatHBoxLayout.addLayout(self.chatVBoxLayout)
        self.sendButton = QtGui.QPushButton(self.chatWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sendButton.sizePolicy().hasHeightForWidth())
        self.sendButton.setSizePolicy(sizePolicy)
        self.sendButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.sendButton.setStyleSheet("border-color: rgba(140, 217, 140, 100);\n"
"border-width: 1px;\n"
"border-style: solid;\n"
"border-radius: 10px;\n"
"background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 white, stop: 1 rgba(140, 217, 140, 255));")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/quip/Images/send-right-32x32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.sendButton.setIcon(icon3)
        self.sendButton.setAutoDefault(False)
        self.sendButton.setDefault(False)
        self.sendButton.setFlat(False)
        self.sendButton.setObjectName("sendButton")
        self.chatHBoxLayout.addWidget(self.sendButton)
        self.gridLayout_2.addLayout(self.chatHBoxLayout, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.chatWidget)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        Chat.setCentralWidget(self.centralwidget)

        self.retranslateUi(Chat)
        QtCore.QMetaObject.connectSlotsByName(Chat)

    def retranslateUi(self, Chat):
        Chat.setWindowTitle(QtGui.QApplication.translate("Chat", "Chat", None, QtGui.QApplication.UnicodeUTF8))
        self.friendCommentTextEdit.setHtml(QtGui.QApplication.translate("Chat", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Droid Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.historyTextBrowser.setHtml(QtGui.QApplication.translate("Chat", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Droid Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:10px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.emoteToolButton.setText(QtGui.QApplication.translate("Chat", "Emoticons", None, QtGui.QApplication.UnicodeUTF8))
        self.transferToolButton.setText(QtGui.QApplication.translate("Chat", "Send File", None, QtGui.QApplication.UnicodeUTF8))
        self.sendButton.setText(QtGui.QApplication.translate("Chat", "Send ", None, QtGui.QApplication.UnicodeUTF8))

from . import quip_qt_rc
