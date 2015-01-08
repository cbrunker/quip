#
# UItility functions used by the Graphic User Interface
#
import asyncio
from PySide import QtGui, QtCore
from lib import Exceptions
from lib.Client import ServerClient, P2PClient
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
            client = ServerClient(profileId, phrase)
            login = asyncio.async(client.login(profileId))
            loop.run_until_complete(login)
            server = runServer(profileId, phrase)
            p2pClient = P2PClient(profileId, phrase)
        except Exceptions.LoginFailure as ex:
            reason = "Login Failed: {}".format(ex)

    # run server with default cert locations
    return client, server, p2pClient, reason

def bytes2human(nbytes):
    suffixes = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')
    if nbytes == 0: return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    return ' '.join((('%.2f' % nbytes).rstrip('0').rstrip('.'), suffixes[i]))

###############
# QT4 specific
###############

def unfade(obj):
    obj.setWindowOpacity(1)

def updateProfile(ui, client):
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
              'comment': ui.commentLineEdit.text()}

    loop = asyncio.get_event_loop()
    set_profile = asyncio.async(client.updateProfile(fields))
    out = loop.run_until_complete(set_profile)

    return out

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