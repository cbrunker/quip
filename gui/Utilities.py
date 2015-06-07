#
# UItility functions used by the Graphic User Interface
#
import asyncio
import logging
from uuid import uuid4
from PySide import QtGui, QtCore
from lib import Exceptions
from lib.Client import ServerClient, P2PClient
from lib.Constants import URL_PATRONAGE
from lib.Server import runServer


def signIn(profileId, phrase):
    """
    Sign in to server and start local server

    @param profileId: user selected profile ID
    @param phrase: Profile ID passphrase
    @return: server client, p2p server, p2p client, failure reason (if failed)
    """
    loop = asyncio.get_event_loop()

    client, server, p2pClient = None, None, None
    reason = ''
    if profileId:
        try:
            client = ServerClient(profileId, phrase, loop=loop)
            loop.run_until_complete(client.login(profileId))
            server = runServer(profileId, phrase)
            p2pClient = P2PClient(profileId, phrase, loop=loop)
        except Exceptions.LoginFailure as ex:
            reason = "Login Failed: {}".format(ex)

    # run server with default cert locations
    return client, server, p2pClient, reason, loop

def bytes2human(nbytes):
    suffixes = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')
    if nbytes == 0: return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    return ' '.join((('%.2f' % nbytes).rstrip('0').rstrip('.'), suffixes[i]))

def emailValidation(email):
    """
    Basic email validation

    @param email: text to validate
    @return: Boolean value based on validity
    """
    if email.count('@') == 1 and len(email.split('.')) > 1 and '@' in email.split('.')[0] and len(email) <= 255:
        return True
    else:
        return False

###############
# QT4 specific
###############

def unfade(obj):
    obj.setWindowOpacity(1)

def updateRemoteProfile(ui, client, loop=None):
    """
    Update profile information for user

    @param ui: user interface window with required object references
    @param client: Server Client object (must be logged in)
    @return: True if updated successfully, otherwise False
    """
    fields = {'first': ui.firstnameLineEdit.text(),
              'last': ui.lastnameLineEdit.text(),
              'alias': ui.aliasLineEdit.text(),
              'city': ui.cityLineEdit.text(),
              'state': ui.stateLineEdit.text(),
              'country': ui.countryLineEdit.text(),
              'comment': ui.commentLineEdit.text(),
              'email': ui.emailLineEdit.text().strip()}

    if not loop:
        loop = asyncio.get_event_loop()

    out = loop.run_until_complete(client.updateProfile(fields))

    return out

def patronWebsite(userId=None):
    """
    Open Patron URL

    @param userId: user ID to provide patronage for
    """
    QtGui.QDesktopServices.openUrl(QtCore.QUrl(URL_PATRONAGE, QtCore.QUrl.StrictMode))

#######################
# Custom UI components
#######################

def messageBox(mtype, text, confirm=False):
    """
    Create a message box with icon, text and OK button.

    @param mtype: message type enum('warning', 'error', 'info')
    @param text: message text to display
    """
    icons = {"warning": ":/quip/Images/dialog-warning.png",
             "info": ":/quip/Images/dialog-information.png",
             "error": ":/quip/Images/dialog-error.png"}

    msgBox = QtGui.QMessageBox()
    # set custom icon
    msgBox.setIconPixmap(icons[mtype])
    msgBox.setText(text)

    if confirm:
        msgBox.addButton(QtGui.QMessageBox.No)
        msgBox.addButton(QtGui.QMessageBox.Yes)

    # change background colour to white
    p = msgBox.palette()
    p.setColor(QtGui.QPalette.Background, QtCore.Qt.white)
    msgBox.setPalette(p)

    # load box, return button pressed
    return msgBox.exec_()


class Background(QtCore.QThread):
    """
    Basic threading worker class to keep UI active
    """

    def __init__(self, function, arguments=None, isFuture=True, loop=None, parent=None):
        """
        Background worker constructor

        @param function: coroutine/future or function to run
        @param arguments: (Optional) function paramater values - does not work with coroutine
        @param isFuture: True if coroutine/future, False for function use
        @param loop: (Optional) Use this loop object instead of creating a new one
        @param parent: (Optional) QT Parent object
        """
        super().__init__(parent)

        self.loop = loop
        self.function = function
        self.arguments = arguments or []
        self.isFuture = isFuture
        self.exiting = False
        self.result = None
        self.workerId = uuid4()

    def run(self):
        # loop has to be created and set (set_event_loop) in this thread before the async() future object is created
        loop = self.loop or asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if self.isFuture:
            #logging.debug("[Thread {}] Initiating asyncio coroutine".format(self.currentThreadId()))
            # run coroutine (auto wraps in asyncio.async()) or future
            self.result = loop.run_until_complete(self.function)
            #logging.debug("[Thread {}] Coroutine complete".format(self.currentThreadId()))
        else:
            #logging.debug("[Thread {}] Initiating function".format(self.currentThreadId()))
            # run function with provided arguments
            try:
                self.result = self.function(*self.arguments)
                #logging.debug("[Thread {}] Function complete".format(self.currentThreadId()))
            except Exception as e:
                self.result = e
                #logging.debug("[Thread {}] Function failed with error: {}".format(self.currentThreadId(), e))
