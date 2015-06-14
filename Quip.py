#!/usr/bin/env python3
#
# GUI Client
#

import sys

if sys.version_info < (3, 4):
    raise Exception("Python Version {!r} found, required version is >= 3.4.0".format(sys.version))

# custom modules
from gui.chat import Ui_Chat
from gui.invites import Ui_Invites
from gui.fileTransfer import Ui_FileTransfers
from gui.profileSearch import Ui_ProfileSearch
from gui.searchResults import Ui_SearchResults
from gui.login import Ui_Login
from gui.newAccount import Ui_NewAccount
from gui.friendList import Ui_FriendList
from gui.friendRequest import Ui_FriendRequest
from gui.profileView import Ui_ProfileView
from gui.accountRecovery import Ui_AccountRecovery
from gui.emoticons import Ui_Emoticons
from gui.settings import Ui_Settings
from gui.Resources import FLAGS, EMOTE_PATTERN, EMOTICONS, RESOURCE_PATTERN, EMOTICON_RESOURCES, URL_PATTERN, Friend, \
    EXT, MIMETYPES
from gui.Utilities import updateRemoteProfile, signIn, messageBox, bytes2human, Background, emailValidation, patronWebsite
from lib.Config import Configuration
from lib import Exceptions
from lib.Constants import STATUS_OFFLINE, STATUS_INVISIBLE, STATUS_AWAY, STATUS_ONLINE, STATUS_BUSY, STATUSES_BASIC, \
    LIMIT_PROFILE_VALUES
from lib.Utils import isValidUUID, checkCerts
from lib.Client import ServerClient
from lib.Database import getProfiles, getAvatar, getFriends, getMasks, updateLocalProfile, delFileRequests, getHistory
from lib.Countries import COUNTRIES

# inbuilt modules
import asyncio
from os import path
from collections import  OrderedDict, Counter
from datetime import datetime
from uuid import uuid4
from hashlib import sha1
from ipaddress import ip_interface
from random import randint
from functools import partial
from time import time

# third-party modules
from PySide import QtCore, QtGui


####################################
# Handlers for UI generated modules
####################################

class FileTransferWindow(QtGui.QMainWindow):
    def __init__(self, p2pClient, server, friends, loop=None, parent=None):
        super().__init__(parent)
        self.ui =  Ui_FileTransfers()
        self.ui.setupUi(self)

        # incoming requests stored in p2p client
        self.p2pClient = p2pClient
        # outgoing requests (stored in server object)
        self.server = server
        self.friends = {f.mask: f for u, f in friends.items()}

        self.loop = loop or asyncio.get_event_loop()

        # actively downloading/uploading
        self.active = []
        # currently listed
        self.current = set()
        # finished downloading/uploading
        self.finished = set()

        self.redraw()

    def redraw(self):
        """
        Check requests and draw file transfer window
        """
        # incoming and outgoing transfers
        transfers = tuple((isIncoming, l.items()) for isIncoming, l in
                          ((bool(n), c) for n, c in enumerate((self.server.fileRequestsOut, self.server.fileRequests))))

        items = set()
        for isIncoming, fileDetails in ((a, f) for a, f in transfers if f):
            for mask, details in fileDetails:
                entry = (mask, tuple(details.keys())[0])
                items.add(entry)

        redraw = self.current != items
        # redraw transfers area only if transfers list changes
        if redraw:
            self.current = items
            # remove all rows as clear() does not
            for r in range(self.ui.transferTableWidget.rowCount()):
                self.ui.transferTableWidget.removeRow(r)

            trow = 0
            # file requests stored in format:  mask-> checksum-> (filename, size, rowid)
            for isIncoming, fileDetails in transfers:
                for trow, (mask, details) in enumerate(fileDetails):
                    self.ui.transferTableWidget.insertRow(trow)
                    checksum = tuple(details.keys())[0]
                    filename, size, rowid = details[checksum]
                    #########################
                    # cell 1 is friend alias
                    #########################
                    qlabel = QtGui.QLabel(self.friends[mask].alias if self.friends[mask].alias else self.friends[mask].uid.decode('ascii'))
                    qlabel.setFocusPolicy(QtCore.Qt.TabFocus)
                    self.ui.transferTableWidget.setCellWidget(trow, 0, qlabel)

                    # column size
                    self.ui.transferTableWidget.setColumnWidth(0, max(self.ui.transferTableWidget.columnWidth(0),
                                                                      min(len(qlabel.text()) * 7, 150)) )

                    ######################
                    # cell 2 file details
                    ######################
                    # use base name as outgoing files will contain path details
                    qlabel = QtGui.QLabel("'{}'   {}".format(path.basename(filename.decode('utf-8') if type(filename) is bytes else filename),
                                                             bytes2human(int(size))))
                    qlabel.setFocusPolicy(QtCore.Qt.TabFocus)
                    self.ui.transferTableWidget.setCellWidget(trow, 1, qlabel)

                    # column size
                    self.ui.transferTableWidget.setColumnWidth(1, max(self.ui.transferTableWidget.columnWidth(1),
                                                                      min(len(qlabel.text()) * 7, 210)))

                    ######################
                    # cell 3 progress bar
                    ######################
                    pbar = QtGui.QProgressBar()
                    pbar.setMaximum(100)
                    pbar.setValue(0)
                    pbar.setDisabled(True)
                    pbar.setMaximumHeight(15)
                    pbar.setFocusPolicy(QtCore.Qt.TabFocus)

                    # widget to hold pbar in the centre
                    widget = QtGui.QWidget()
                    widget.setFocusPolicy(QtCore.Qt.TabFocus)
                    layout = QtGui.QHBoxLayout(widget)
                    layout.addWidget(pbar)
                    layout.setAlignment(QtCore.Qt.AlignCenter)
                    layout.setContentsMargins(4, 4, 4, 4)
                    widget.setLayout(layout)

                    self.ui.transferTableWidget.setCellWidget(trow, 2, widget)

                    ############################
                    # Accept and Cancel buttons
                    ############################
                    # cell 5 cancel button created here for sizepolicy reuse
                    cancelButton = QtGui.QPushButton(QtGui.QIcon(QtGui.QPixmap(":/quip/Images/stop.png")), '')

                    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
                    sizePolicy.setHorizontalStretch(0)
                    sizePolicy.setVerticalStretch(0)
                    sizePolicy.setHeightForWidth(cancelButton.sizePolicy().hasHeightForWidth())

                    if isIncoming:
                        acceptButton = QtGui.QPushButton(QtGui.QIcon(QtGui.QPixmap(":/quip/Images/tick.png")), '')
                        acceptButton.setSizePolicy(sizePolicy)
                        acceptButton.setStyleSheet("border-color: rgba(140, 217, 140, 100);\n"
                                                            "border-width: 1px;\n"
                                                            "border-style: solid;\n"
                                                            "border-radius: 10px;\n"
                                                            "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, "
                                                            "stop: 0 white, stop: 1 rgba(140, 217, 140, 100));")
                        acceptButton.setFlat(True)
                        acceptButton.setFocusPolicy(QtCore.Qt.TabFocus)
                        acceptButton.clicked.connect(partial(self.retrieveFile, trow, mask, checksum, size))
                        self.ui.transferTableWidget.setCellWidget(trow, 3, acceptButton)
                        # accept button and signal only available for incoming files
                        #self.ui.transferTableWidget.cellWidget(trow, 3).clicked.connect(self.transferFile)

                    # cell 5 cancel/reject button
                    cancelButton.setSizePolicy(sizePolicy)
                    cancelButton.setStyleSheet("border-color: rgba(255, 0, 0, 150);\n"
                                                "border-width: 1px;\n"
                                                "border-style: solid;\n"
                                                "border-radius: 10px;\n"
                                                "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, "
                                                "stop: 0 white, stop: 1 rgba(255, 0, 0, 100));")
                    cancelButton.setFlat(True)
                    cancelButton.setFocusPolicy(QtCore.Qt.TabFocus)
                    # cancel transfer signal
                    cancelButton.clicked.connect(partial(self.cancelTransfer, isIncoming, rowid))
                    self.ui.transferTableWidget.setCellWidget(trow, 4, cancelButton)

            trow = trow + 1 if transfers else trow
            # if there are any completed files, draw them here
            for frow, (isIncoming, mask, location, size) in enumerate(self.finished):
                tableRow = trow + frow
                self.ui.transferTableWidget.insertRow(tableRow)
                #########################
                # cell 1 is friend alias
                #########################
                qlabel = QtGui.QLabel(self.friends[mask].alias if self.friends[mask].alias else self.friends[mask].uid.decode('ascii'))
                qlabel.setFocusPolicy(QtCore.Qt.TabFocus)
                self.ui.transferTableWidget.setCellWidget(tableRow, 0, qlabel)

                # column size
                self.ui.transferTableWidget.setColumnWidth(0, max(self.ui.transferTableWidget.columnWidth(0),
                                                                  min(len(qlabel.text()) * 7, 150)) )

                ######################
                # cell 2 file details
                ######################
                qlabel = QtGui.QLabel("'{}'   {}".format(path.basename(location), bytes2human(int(size))))
                qlabel.setFocusPolicy(QtCore.Qt.TabFocus)
                self.ui.transferTableWidget.setCellWidget(tableRow, 1, qlabel)

                # column size
                self.ui.transferTableWidget.setColumnWidth(1, max(self.ui.transferTableWidget.columnWidth(1),
                                                                  min(len(qlabel.text()) * 7, 210)))

                #############################
                # cell 3 is open file button
                #############################
                openButton = QtGui.QPushButton(QtGui.QIcon(path.join(EXT, '{}.png'.format(MIMETYPES.get(path.splitext(location)[1], 'unknown')))), 'Open File')
                openButton.setStyleSheet("border-color: rgba(140, 217, 140, 100);\n"
                                        "border-width: 1px;\n"
                                        "border-style: solid;\n"
                                        "border-radius: 5px;\n"
                                        "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, "
                                        "stop: 0 white, stop: 1 rgba(140, 217, 140, 100));")
                openButton.setFocusPolicy(QtCore.Qt.TabFocus)
                openButton.clicked.connect(partial(self.openFile, location))
                widget = QtGui.QWidget()
                widget.setFocusPolicy(QtCore.Qt.TabFocus)
                layout = QtGui.QHBoxLayout(widget)
                layout.addWidget(openButton)
                layout.setAlignment(QtCore.Qt.AlignCenter)
                layout.setContentsMargins(4, 4, 4, 4)
                widget.setLayout(layout)

                self.ui.transferTableWidget.setCellWidget(tableRow, 2, widget)

        if self.ui.transferTableWidget.rowCount():
            # accept button column width
            self.ui.transferTableWidget.setColumnWidth(3, 40)
            # set cancel button column width
            self.ui.transferTableWidget.setColumnWidth(4, 40)
            # progress bar has variable width to ensure last column stays at set width
            self.ui.transferTableWidget.setColumnWidth(2, self.width() - sum(self.ui.transferTableWidget.columnWidth(c) for c in (0, 1, 3, 4)) - 6)

        return redraw

    def retrieveFile(self, tableRow, mask, checksum, size):
        """
        Accept file and attempt retrieval from destination

        @param tableRow: table row
        @param mask: friend mask
        @param checksum: file checksum
        """
        # progress bar
        pbar = self.ui.transferTableWidget.cellWidget(tableRow, 2).children()[1]
        # basic processing
        pbar.setMaximum(0)

        location = ''
        retrieve_file = self.p2pClient.retrieveFile(self.friends[mask].uid, checksum)
        try:
            location = self.loop.run_until_complete(retrieve_file)
        except Exceptions.ConnectionFailure:
            # friend may have changed address, contact server for updated details
            details = self.loop.run_until_complete(self.client.getDetails((self.friend.mask,)))
            if len(details) > 1:
                # if we have a valid server response, update local details
                self.p2pClient.friends[self.friend.uid] = details[self.friend.mask][1]

                try:
                    location = self.loop.run_until_complete(retrieve_file)
                except Exceptions.ConnectionFailure:
                    # friend uncontactable
                    messageBox("error", "Request Failed: Unable to contact friend")
                except Exceptions.FileCorruption as e:
                    messageBox("warning", str(e))
                    self.server.fileRequests.reload()
        except Exceptions.FileCorruption as e:
                    messageBox("warning", str(e))
                    self.server.fileRequests.reload()

        if path.isfile(location):
            # successfully downloaded
            isIncoming = True if self.ui.transferTableWidget.cellWidget(tableRow, 3) else False

            if isIncoming:
                # delete accept button
                self.ui.transferTableWidget.removeCellWidget(tableRow, 3)
            # delete cancel/reject button
            self.ui.transferTableWidget.removeCellWidget(tableRow, 4)

            self.ui.transferTableWidget.removeCellWidget(tableRow, 2)

            openButton = QtGui.QPushButton(QtGui.QIcon(path.join(EXT,'{}.png'.format(MIMETYPES.get(path.splitext(location)[1], 'unknown')))), 'Open File')
            openButton.setStyleSheet("border-color: rgba(140, 217, 140, 100);\n"
                                    "border-width: 1px;\n"
                                    "border-style: solid;\n"
                                    "border-radius: 5px;\n"
                                    "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, "
                                    "stop: 0 white, stop: 1 rgba(140, 217, 140, 100));")
            openButton.setFocusPolicy(QtCore.Qt.TabFocus)
            openButton.clicked.connect(partial(self.openFile, location))
            widget = QtGui.QWidget()
            widget.setFocusPolicy(QtCore.Qt.TabFocus)
            layout = QtGui.QHBoxLayout(widget)
            layout.addWidget(openButton)
            layout.setAlignment(QtCore.Qt.AlignCenter)
            layout.setContentsMargins(4, 4, 4, 4)
            widget.setLayout(layout)

            self.ui.transferTableWidget.setCellWidget(tableRow, 2, widget)

            self.finished.add((isIncoming, mask, location, size))
        else:
            pbar.setMinimum(0)
            pbar.setMaximum(100)

    def cancelTransfer(self, isIncoming, storageRow):
        """
        Cancel/Deline transfer, delete local storage information.

        @param isIncoming: True fif incoming transfer request, False if outgoing transfer request
        @param storageRow: Row ID of transfer entry in local database
        """
        delFileRequests(storageRow)
        if isIncoming:
            self.server.fileRequests.reload()
        else:
            self.server.fileRequestsOut.reload()

        self.redraw()

    @staticmethod
    def openFile(filePath):
        # qt4 doesn't accept windows path sep
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("file:///{}".format(filePath.replace('\\', '/')), QtCore.QUrl.TolerantMode))

class ProfileView(QtGui.QMainWindow):
    def __init__(self, avatar, profile, client=None, p2pclient=None, callback=None, loop=None, parent=None):
        """
        Display profile data

        @param avatar: avatar QPixmap object
        @param profile: profile dict as returned by server
        @param client: (optional) Server client. Should only be given if viewing logged in profile
        @param p2pclient: (optional) P2P client. Should only be given if viewing logged in profile
        @param callback: (optional) method or function to call on close
        """
        super().__init__(parent)
        self.ui =  Ui_ProfileView()
        self.ui.setupUi(self)

        self.loop = loop or asyncio.get_event_loop()
        self.profile = profile
        self.client = client
        self.p2pclient = p2pclient
        self.callback = callback

        self.avatar = avatar

        self.reference = {self.ui.aliasLineEdit: 'alias',
                          self.ui.firstnameLineEdit: 'first',
                          self.ui.lastnameLineEdit: 'last',
                          self.ui.commentLineEdit: 'comment',
                          self.ui.cityLineEdit: 'city',
                          self.ui.stateLineEdit: 'state',
                          self.ui.countryLineEdit: 'country',
                          self.ui.emailLineEdit: 'email'}

        self.origStyleEmail = self.ui.emailLineEdit.styleSheet()
        self.origTextEmail = self.ui.emailLineEdit.placeholderText()

        # signals and slots
        self.ui.addAvatarButton.clicked.connect(self.newAvatar)
        self.ui.saveButton.clicked.connect(self.saveProfile)
        self.ui.patronButton.clicked.connect(patronWebsite)
        self.ui.emailLineEdit.selectionChanged.connect(self.reset)
        self.ui.profileLabel.setFocus()

        self.drawProfile()

    def reset(self):
        """
        Reset email placeholder text and stylesheet
        """
        if self.ui.emailLineEdit.placeholderText() != self.origTextEmail:
            self.ui.emailLineEdit.setStyleSheet(self.origStyleEmail)
            self.ui.emailLineEdit.setPlaceholderText(self.origTextEmail)

    def newAvatar(self):
        avatar = QtGui.QFileDialog.getOpenFileName(self, "Open Image", '', "Image Files (*.png *.jpg *.bmp)")[0]

        if avatar:
            image = QtGui.QImage(avatar, format=QtGui.QImage.Format_ARGB32_Premultiplied)
            avatar = image.scaled(64, 64, mode=QtCore.Qt.SmoothTransformation)
            self.avatar = QtGui.QPixmap.fromImage(avatar)
            self.ui.avatarLabel.setPixmap(self.avatar)

    def saveProfile(self):
        """
        Save any profile changes
        """
        if len(self.ui.emailLineEdit.text().strip()) and not emailValidation(self.ui.emailLineEdit.text().strip()):
            self.reset()
            # entered email is invalid
            self.ui.emailLineEdit.setText("")
            self.ui.emailLineEdit.setPlaceholderText("Invalid e-mail address")
            self.ui.emailLineEdit.setStyleSheet("background-color: rgba(225, 33, 33, 100);")
            self.ui.commentLineEdit.setFocus()
        else:
            # save any avatar changes
            if self.avatar:
                ba = QtCore.QByteArray()
                buffer = QtCore.QBuffer(ba)
                self.avatar.save(buffer, 'PNG')
                data = ba.data()

                # save locally
                updateLocalProfile(self.client.safe, self.client.profileId, data, self.ui.aliasLineEdit.text())
            else:
                updateLocalProfile(self.client.safe, self.client.profileId, alias=self.ui.aliasLineEdit.text())

            # send profile changes to server
            updateRemoteProfile(self.ui, self.client, loop=self.loop)

            # will call drawProfile() for friendList avatar redraw
            self.callback()
            self.close()

    def drawProfile(self):
        for widget, field in self.reference.items():
            widget.setText(self.profile[field])

        if self.avatar:
            self.ui.avatarLabel.setPixmap(self.avatar)

        hasPatron = False

        if self.client:
            # viewing our own profile
            for w in self.reference.keys():
                w.setReadOnly(False)
                w.setFocusPolicy(QtCore.Qt.StrongFocus)

            self.ui.useridLabelText.setText(self.client.uid.decode('ascii'))
            alias = self.profile['alias'] or self.client.uid.decode('ascii')
            self.ui.patronTimeLabel.setText(datetime.fromtimestamp(float(self.profile['patron'])).strftime('%I:%M%p %dth %b %y UTC'))

            if (float(self.profile['patron']) - time()) > 0:
                hasPatron = True

        else:
            # viewing friend/contact profile
            # do not show email area for friends
            self.ui.emailLabel.hide()
            self.ui.emailLineEdit.hide()
            # do not show patron end time for friends
            self.ui.patronTimeLabel.hide()
            # ensure mutable options are disabled or hidden
            self.ui.addAvatarButton.hide()
            self.ui.saveButton.hide()
            # add alias and ID information
            self.ui.useridLabelText.setText(self.profile['uid'])
            alias = self.profile['alias'] or self.profile['uid']

            # display patron star if patron status confirmed
            if int(self.profile['patron']) > 0:
                hasPatron = True

        if hasPatron:
            patronIcon = QtGui.QIcon()
            patronIcon.addPixmap(QtGui.QPixmap(":/quip/Images/patron.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.ui.patronButton.setIcon(patronIcon)

        self.ui.useridLabelText.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.ui.profileLabel.setText("{}'s Profile".format(alias))


class FriendRequest(QtGui.QWidget):

    def __init__(self, client, p2pclient, callback, requests=None, loop=None, parent=None):
        """
        Friend request window constuctor

        @param client: server client object
        @param p2pclient: p2p client object
        @param callback: callable method belonging to parent object
        @param requests: (optional) friend requests. Avoids loading friend requests in constructor
        @param parent: (optional) passed to inherited class
        """
        super().__init__(parent)
        self.ui =  Ui_FriendRequest()
        self.ui.setupUi(self)

        # final requests for recursive functions
        self._final = False
        self.client = client
        self.p2pclient = p2pclient
        # currently displayed potential friend's user ID
        self.uid = None
        # online status of potential friend
        self.status = None
        # obtained profile information
        self.profile = None
        # load requests
        self.loop = loop or asyncio.get_event_loop()
        # redraw friendlist
        self.callback = callback

        if requests is None:
            self.requests = self.loop.run_until_complete(self.client.getRequests())
        else:
            self.requests = requests

        self.next = (u for u in self.requests.keys())

        self.ui.progressBar.hide()
        # signals and slots
        self.ui.acceptButton.clicked.connect(self.attemptFriendship)
        self.ui.ignoreButton.clicked.connect(self.deleteRequest)
        # currently the block button will just delete the request
        self.ui.blockButton.clicked.connect(self.deleteRequest)
        self.ui.nextButton.clicked.connect(self.nextRequest)

        self.ui.avatarLabel.setFocus()
        # display request
        self.nextRequest()

    def deleteRequest(self, done=True):
        del_request = self.client.delRequest(self.uid, rowid=self.requests[self.uid][-1])
        self.loop.run_until_complete(del_request)
        if done:
            self.nextRequest()

    def attemptFriendship(self):
        # attempt to gather details from already loaded data
        msg, addr, status, rid = self.requests[self.uid]
        # mhash will be of the logged in user's ID and the sent message
        mhash = bytes(sha1(b''.join((self.client.uid, bytes(msg, encoding='utf-8')))).hexdigest(), encoding='ascii')

        # show processing animation
        self.ui.progressBar.show()
        self.background = Background(self.p2pclient.friendCompletion(self.uid, mhash=mhash, address=addr))
        self.background.finished.connect(self._friendshipResult)
        self.background.start()
        self.ui.progressBar.show()

    def _friendshipResult(self):
        # attempt connection using last known address (locally stored)
        if self.background.result:
            success, token = self.background.result
        else:
            success = None
            token = None

        if success:
            success = self.loop.run_until_complete(self.client.addAuthorisationToken(token=token))
        else:
            # refresh requests from server, will contain current address information
            self.requests = self.loop.run_until_complete(self.client.getRequests())
            if not self._final:
                self.attemptFriendship()
            else:
                # reset final flag
                self._final = False

        # no longer processing
        self.ui.progressBar.hide()

        if success:
            # delete request locally and remotely
            self.deleteRequest(done=False)
            messageBox('info', 'Successfully added friend')
            # redraw friend list
            self.callback(retry=True)
            self.nextRequest()
        else:
            messageBox('warning', 'Unable to complete friend request. Try again later')

    def nextRequest(self):
        """
        Display details of next friend request
        """
        try:
            self.uid = next(self.next)
        except StopIteration:
            # only display message if friend requests exist
            if self.uid is not None:
                messageBox('info', 'All friend requests completed')
            self.close()
            return

        msg, status, addr, rowid = self.requests[self.uid]

        if status == STATUS_OFFLINE:
            self.ui.statusLabel.show()
            self.ui.acceptButton.setDisabled(True)
            self.ui.acceptButton.setToolTip("User must be online to accept")
        else:
            self.ui.statusLabel.hide()
            self.ui.acceptButton.setDisabled(False)
            self.ui.acceptButton.setToolTip(None)

        get_profile = self.client.getProfile(self.uid)
        self.profile = self.loop.run_until_complete(get_profile)

        self.ui.aliasLabel.setText('{} ({})'.format(self.profile['alias'], self.uid))
        self.ui.messagePlainTextEdit.setPlainText(self.requests[self.uid][0])


class ResultsWindow(QtGui.QMainWindow):
    def __init__(self, alias, client, profiles, cursor, previous=0, loop=None, parent=None):
        """
        Profile Search Results window

        @param client: server client object
        @param profiles: returned profiles from search
        @param cursor: cursor point for continuing search
        @param previous: previously returned profiles for this search
        """
        super().__init__(parent)
        self.ui =  Ui_SearchResults()
        self.ui.setupUi(self)

        self.loop = loop or asyncio.get_event_loop()
        self.alias = alias
        self.profiles = profiles
        self.client = client
        self.cursor = cursor
        self.previous = previous
        self.sortedBy = sorted(LIMIT_PROFILE_VALUES.keys())

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.ui.comboBox.addItems(self.sortedBy)
        self.ui.countLabel.setText(" to ".join((str(previous), str(len(profiles) + previous))))

        # first set of results being displayed
        if previous == 0:
            self.ui.previousButton.setDisabled(True)

        # no more results available
        if cursor == '0':
            self.ui.moreButton.setDisabled(True)

        # no results
        if not self.profiles:
            self.ui.addContactButton.setDisabled(True)

        # signals and slots
        self.ui.comboBox.currentIndexChanged.connect(self.reload)
        self.ui.addContactButton.clicked.connect(self.requestFriends)

        self.reload()

        self.ui.searchLabel.setFocus()

    def requestFriends(self):
        """
        Initiate friend requests for selected profiles
        """
        # friend request message entered by user
        message = self.ui.messageLineEdit.text()
        if not message:
            # friend message input if none exists, contains random element for hash verification uniqueness
            message = "{} requests to be your friend. Seed: {}".format(self.alias, str(uuid4()))


        failed = []
        count = 0
        model = self.ui.profilesListView.model()
        # cycle through all checked profiles
        for uid in (self.profiles[r]['uid'] for r in (r for r in range(model.rowCount()) if model.item(r).checkState() == QtCore.Qt.Checked)):
            count += 1
            # send friend request
            out = self.loop.run_until_complete(self.client.friendRequest(uid, message))
            if not out:
                # notify user not all requests were sent successfully
                failed.append(uid)

        if not count:
            text = "No contacts selected, please select a contact from the list"
            mtype = "warning"
        elif not failed:
            text = "All {} friend request(s) successfully sent".format(count)
            mtype = "info"
        else:
            text = "Error: {} out of {} friend request(s) failed to send".format(len(failed), count)
            mtype = "error"

        messageBox(mtype, text)


    def reload(self):
        """
        Reload profiles, sorting by current sort value
        """
        # sort profile data
        self.profiles = sorted(self.profiles, key=lambda x: x[self.sortedBy[self.ui.comboBox.currentIndex()]])
        self._listProfiles()

    def _listProfiles(self):
        try:
            model = self.ui.profilesListView.model()
            # ensure the model containing the items is clear
            model.clear()
        except AttributeError:
            # create the model if this is the first time listing
            model = QtGui.QStandardItemModel(self.ui.profilesListView)

        if not self.profiles:
             model.appendRow(QtGui.QStandardItem("No Matches Found"))
        else:
            for r, p in enumerate(self.profiles):
                # text layout format
                txt = '{}\n\t{} {}\n\t{}'.format(p['alias'] if p['alias'] else p['uid'].decode('ascii'),
                                                 p['first'], p['last'], p['comment'])

                try:
                    flag = COUNTRIES[p['country'].lower().strip()]
                except KeyError:
                    flag = 'unknown'

                item = QtGui.QStandardItem(QtGui.QIcon(path.join(FLAGS,'{}.png'.format(flag))), txt)

                item.setEditable(False)
                item.setCheckable(True)

                model.appendRow(item)

        self.ui.profilesListView.setModel(model)

class ProfileSearchWindow(QtGui.QMainWindow):
    def __init__(self, alias, client, loop=None, parent=None):
        """
        Profile Search Window constructor

        @param alias: logged in user's alias
        @param client: server client object
        """
        super().__init__(parent)
        self.ui =  Ui_ProfileSearch()
        self.ui.setupUi(self)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.loop = loop or asyncio.get_event_loop()
        # alias is used in sending default message in results window (friend request)
        self.alias = alias
        self.client = client
        self.origSytle = self.ui.useridLineEdit.styleSheet()
        self.origText = self.ui.useridLineEdit.placeholderText()

        # profile search field line edit object reference
        self.reference = {self.ui.aliasLineEdit: 'alias',
                          self.ui.firstnameLineEdit: 'first',
                          self.ui.lastnameLineEdit: 'last',
                          self.ui.commentLineEdit: 'comment',
                          self.ui.cityLineEdit: 'city',
                          self.ui.stateLineEdit: 'state',
                          self.ui.countryLineEdit: 'country'}

        # signals
        self.ui.useridLineEdit.selectionChanged.connect(self.reset)
        self.ui.useridLineEdit.returnPressed.connect(self.findProfiles)
        self.ui.searchProfilesButton.clicked.connect(self.findProfiles)

    def reset(self):
        self.ui.useridLineEdit.setStyleSheet(self.origSytle)
        self.ui.useridLineEdit.setPlaceholderText(self.origText)

    def findProfiles(self):
        uid = self.ui.useridLineEdit.text()
        if uid and (len(uid) != 36 or not isValidUUID(uid)):
            self.ui.useridLineEdit.setText("")
            self.ui.useridLineEdit.setStyleSheet("background-color: rgba(225, 33, 33, 100);")
            self.ui.useridLineEdit.setPlaceholderText("Invalid User ID Format. Example: 684e32e0-7422-4dab-904c-0a08db506d89")
            self.ui.searchDetailsPlainTextEdit.setFocus()
            return

        self.reset()
        fields = {f: v.text() for v, f in self.reference.items() if v.text()}

        if not fields and not uid:
            return

        if not uid:
            cursor, found, uids = self.loop.run_until_complete(self.client.profileSearch(fields))
        else:
            cursor = '0'
            uids = [uid]

        profiles = []
        for uid in uids:
            # valid user ID entered, request profile directly based on entered user id
            profile = self.loop.run_until_complete(self.client.getProfile(uid))
            # add UID for contact addition
            profile['uid'] = uid
            profiles.append(profile)

        self._results = ResultsWindow(self.alias, self.client, profiles, cursor, loop=self.loop)
        self._results.show()

class SettingsWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =  Ui_Settings()
        self.ui.setupUi(self)

        self.config = Configuration()
        self.ui.stackedWidget.setCurrentIndex(0)
        self._pages = {'network': 0, 'storage': 1, 'encryption': 2}

        # fill pages with data
        self.setSettingsContent()

        ##########
        # Signals
        ##########
        # stacked widget change via action bar buttons
        self.ui.actionNetwork.triggered.connect(self.choosePage)
        self.ui.actionStorage.triggered.connect(self.choosePage)
        self.ui.actionEncryption.triggered.connect(self.choosePage)

        # network page signals
        self.ui.ipAdressLineEdit.returnPressed.connect(self.saveConfig)
        self.ui.ipAdressLineEdit.selectionChanged.connect(self.noStyle)
        self.ui.portLineEdit.returnPressed.connect(self.saveConfig)
        self.ui.portLineEdit.selectionChanged.connect(self.noStyle)
        self.ui.protocolTimeoutLineEdit.returnPressed.connect(self.saveConfig)
        self.ui.protocolTimeoutLineEdit.selectionChanged.connect(self.noStyle)
        self.ui.fileTransferLineEdit.returnPressed.connect(self.saveConfig)
        self.ui.fileTransferLineEdit.selectionChanged.connect(self.noStyle)
        self.ui.chunkSizeLineEdit.returnPressed.connect(self.saveConfig)
        self.ui.chunkSizeLineEdit.selectionChanged.connect(self.noStyle)
        self.ui.portRandomiseButton.clicked.connect(self.randomPort)

        # storage signals
        self.ui.downloadButton.clicked.connect(self.chooseDirectory)
        self.ui.fileTransferLimitSpinBox.valueChanged.connect(self.saveConfig)
        self.ui.friendRequestLimitSpinBox.valueChanged.connect(self.saveConfig)
        self.ui.verifyCheckbox.stateChanged.connect(self.saveConfig)

        self.ui.downloadLabel.setFocus()

    def chooseDirectory(self):
        location = QtGui.QFileDialog.getExistingDirectory(self, "Choose Directory", '', QtGui.QFileDialog.ShowDirsOnly |
                                                          QtGui.QFileDialog.DontResolveSymlinks)
        if location:
            self.ui.downloadLineEdit.setText(location)
            self.saveConfig(self.ui.downloadLineEdit)

    def randomPort(self):
        self.ui.portLineEdit.setText(str(randint(1025, 65534)))
        self.saveConfig(self.ui.portLineEdit)

    def noStyle(self):
        widget = self.sender()
        widget.setStyleSheet("")
        widget.setPlaceholderText('')

    def saveConfig(self, widget=None):
        """
        Validates and saves all setting changes to config file
        """
        placeholder = ''
        invalid = False

        if widget is None:
            # widget which triggered
            widget = self.sender()

        if widget == self.ui.ipAdressLineEdit:
            try:
                self.config.host = str(ip_interface(widget.text())) if widget.text() else ''
            except ValueError:
                invalid = True
                placeholder = 'Invalid IP format. Examples: 192.168.1.1'
                widget.setPlaceholderText('Invalid IP format. Examples: 192.168.1.1')
        elif widget in (self.ui.portLineEdit, self.ui.fileTransferLineEdit, self.ui.protocolTimeoutLineEdit,
                        self.ui.chunkSizeLineEdit):
            # integer line edit parse
            try:
                number = str(int(widget.text()))
            except ValueError:
                placeholder = '{} is not a valid number'.format(widget.text())
                invalid = True

            if not invalid:
                if widget == self.ui.portLineEdit:
                    self.config.tcp = number
                elif widget == self.ui.protocolTimeoutLineEdit:
                    self.config.idle_timeout = number
                elif widget == self.ui.chunkSizeLineEdit:
                    self.config.max_chunk = number
                else:
                    self.config.file_timeout = number
        elif widget == self.ui.friendRequestLimitSpinBox:
            self.config.request_expiry = str(widget.value())
        elif widget == self.ui.fileTransferLimitSpinBox:
            self.config.file_expiry = str(widget.value())
        elif widget == self.ui.downloadLineEdit:
            self.config.download_directory = widget.text()
        elif widget == self.ui.verifyCheckbox:
            self.config.verify = str(int(self.ui.verifyCheckbox.checkState()))

        if invalid:
            try:
                # set highlighted placeholder data where applicable
                widget.setText("")
                widget.setPlaceholderText(placeholder)
                widget.setStyleSheet("background-color: rgba(225, 33, 33, 100);")
            except Exception:
                return
        else:
            try:
                # remove style and placeholder
                widget.setStyleSheet("")
                widget.setPlaceholderText('')
            except Exception:
                pass

            self.config.save()

        self.ui.downloadLabel.setFocus()

    def choosePage(self):
        self.ui.stackedWidget.setCurrentIndex(self._pages[self.sender().text().lower()])

    def setSettingsContent(self):
        # network
        self.ui.ipAdressLineEdit.setText(self.config.host)
        self.ui.portLineEdit.setText(self.config.tcp)
        self.ui.protocolTimeoutLineEdit.setText(self.config.idle_timeout)
        self.ui.fileTransferLineEdit.setText(self.config.file_timeout)
        self.ui.chunkSizeLineEdit.setText(self.config.max_chunk)

        # storage
        self.ui.downloadLineEdit.setText(self.config.download_directory)
        self.ui.verifyCheckbox.setChecked(int(self.config.verify))
        self.ui.friendRequestLimitSpinBox.setValue(int(self.config.request_expiry))
        self.ui.fileTransferLimitSpinBox.setValue(int(self.config.file_expiry))


class EmoticonWindow(QtGui.QWidget):
    def __init__(self, callback, parent=None):
        super().__init__(parent)
        self.ui =  Ui_Emoticons()
        self.ui.setupUi(self)

        self.callback = callback

        # signals
        self.ui.emoticonTable.cellClicked.connect(self.chooseEmoticon)

    def chooseEmoticon(self, row, col):
        icon = self.ui.emoticonTable.item(row, col)
        self.callback(icon.toolTip())

class ChatWindow(QtGui.QMainWindow):
    def __init__(self, alias, friend, profile, p2pClient, client, callback, serverCallback, ignore=None, loop=None, parent=None):
        super().__init__(parent)
        self.ui =  Ui_Chat()
        self.ui.setupUi(self)

        # ignore the following ids from history output, allows for new messages to be displayed
        ignore = ignore or []
        # background worker pointers
        self._background = {}
        # alias of logged in user
        self.alias = alias
        # friend object of chat window
        self.friend = friend
        # friend's profile
        self.profile = profile
        # p2p client for p2p communication
        self.p2pClient = p2pClient
        # server client (address lookup)
        self.client = client
        # transfer window
        self.callback = callback
        # server transfers reload
        self.serverCallback = serverCallback

        self.loop = loop or asyncio.get_event_loop()

        # styling override for chat history area
        css = "p { margin-top:0px; margin-bottom:10px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; white-space: pre-wrap;}"
        baseHtml = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
<link rel='stylesheet' type='text/css' href='chat.css'>
</style></head><body style=" font-family:'Droid Sans'; font-size:10pt; font-weight:400; font-style:normal;">
<p><br /></p></body></html>"""
        document = QtGui.QTextDocument()
        document.addResource(QtGui.QTextDocument.StyleSheetResource, QtCore.QUrl('chat.css'), css)
        document.setHtml(baseHtml)

        self.ui.historyTextBrowser.setDocument(document)
        self.ui.historyTextBrowser.show()

        # colour of logged in user timestamp and name
        self.colour = '#0055ff'
        # colour of friend's timestamp and name
        self.friendColour = '#dc0000'
        # comment colour
        self.commentColour = '#8d8d8d'
        # offline colour
        self.offlineColour = '#d9d9d9'
        # transfer colour
        self.transferColour = '#228B22'
        # breaks
        space = '&nbsp;'
        # base template layout
        self.templateBase = """<span style=" color: {};">positional{}{}{}</span><span style=" color:#000000;">positional</span>"""
        # format template for outgoing messages (sent by logged in user)
        self.templateOut = self.templateBase.format(self.colour, space * 7, self.alias,
                                                    space * (LIMIT_PROFILE_VALUES['alias'] - len(self.alias))).replace("positional", "{}")
        # format template for incoming messages
        self.templateIn = self.templateBase.format(self.friendColour, space * 7, self.friend.alias,
                                                   space * (LIMIT_PROFILE_VALUES['alias'] - len(self.friend.alias))).replace("positional", "{}")
        # format offline sent messages
        self.templateOff = self.templateBase.format(self.offlineColour, space * 7, self.alias,
                                                    space * (LIMIT_PROFILE_VALUES['alias'] - len(self.alias))).replace("positional", "{}")
        # format file transfer
        self.templateTransfer = """<span style=" color: {};">File transfer request for 'positional' sent to positional at positional</span>""".format(self.transferColour).replace("positional", "{}")

        self.statusColour = {STATUS_ONLINE: ('255, 255, 255', 100),
                             STATUS_AWAY: ('255, 170, 0', 100),
                             STATUS_BUSY: ('255, 0, 0', 100),
                             STATUS_INVISIBLE: ('167, 167, 167', 100)}

        self._emoteWindow = None

        # check if friend/contact has patron status
        if int(self.profile['patron']) > 0:
            patronIcon = QtGui.QIcon()
            patronIcon.addPixmap(QtGui.QPixmap(":/quip/Images/patron.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.ui.patronButton.setIcon(patronIcon)

        ####################
        # Signal connectors
        ####################
        self.ui.sendButton.clicked.connect(self.prepareMessage)
        self.ui.chatTextEdit.installEventFilter(self)
        self.ui.emoteToolButton.clicked.connect(self.emoticonWindow)
        #self.ui.chatTextEdit.returnPressed.connect(self.sendMessage)
        self.ui.transferToolButton.clicked.connect(self.selectTransferFile)
        self.ui.patronButton.clicked.connect(patronWebsite)

        # ui customisation
        self.setDetails()
        self.setAvatar()
        self.setStatus()

        # draw previous history
        history = getHistory(self.client.safe, self.client.profileId, self.friend.mask)
        for recevied, msg, tstamp in ((r, m, t) for rowid, r, m, t in history if rowid not in ignore):
            name = self.friend.alias if recevied else self.alias
            # format history messages
            historyFormat = self.templateBase.format(self.offlineColour, space * 7,
                                                     name,
                                                     space * (LIMIT_PROFILE_VALUES['alias'] - len(name))).replace("positional", "{}")
            self.ui.historyTextBrowser.append(historyFormat.format(tstamp, msg.replace('\n', '<br />')))

        # ensure the msg area has foxus
        self.ui.chatTextEdit.setFocus()

    def eventFilter(self, widget, event):
        """
        Allows SHIFT+ENTER to insert new lines in chat text area without submitting message.
        Supports emoticon insertion.
        """
        if event.type() == QtCore.QEvent.KeyPress and widget is self.ui.chatTextEdit:
            key = event.key()
            if key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter) and event.modifiers() != QtCore.Qt.ShiftModifier:
                self.prepareMessage()
                return True
            elif key == QtCore.Qt.Key_Space:
                # check for emoticons when space is pressed
                text = self.ui.chatTextEdit.toHtml()
                found = False
                for emote in EMOTE_PATTERN.findall(text):
                    try:
                        text = text.replace(emote, '<img src="{}" />'.format(EMOTICONS[emote]))
                    except KeyError:
                        continue
                    found = True

                if found:
                    self.ui.chatTextEdit.setHtml(text)
                    self.ui.chatTextEdit.moveCursor(QtGui.QTextCursor.End)
                    return True

        return QtGui.QWidget.eventFilter(self, widget, event)

    def selectTransferFile(self):
        filePath = QtGui.QFileDialog.getOpenFileName(self, "Select File", '')[0]
        if filePath:
            # submit file transfer request
            file_request = self.p2pClient.sendFileRequest(self.friend.uid, filePath)

            success = False
            try:
                success = self.loop.run_until_complete(file_request)
            except Exceptions.ConnectionFailure:
                # friend may have changed address, contact server for updated details
                details = self.loop.run_until_complete(self.client.getDetails((self.friend.mask,)))
                if len(details) > 1:
                    # if we have a valid server response, update local details
                    self.p2pClient.friends[self.friend.uid] = details[self.friend.mask][1]

                    try:
                        success = self.loop.run_until_complete(file_request)
                    except Exceptions.ConnectionFailure:
                        # friend uncontactable
                        success = False

            if success:
                # show file transfer request in chat history window
                self.ui.historyTextBrowser.append(self.templateTransfer.format(path.basename(filePath),
                                                  self.friend.alias if self.friend.alias else self.friend.uid.decode('ascii'),
                                                  datetime.now().strftime("%I:%M:%p")))
                self.serverCallback()
            else:
                messageBox("error", "Request Failed: Unable to contact friend")


    def setDetails(self):
        self.setWindowTitle(self.friend.alias if self.friend.alias else self.friend.uid.decode('ascii'))
        # handle status background
        self.ui.friendAliasLineEdit.setText(self.friend.alias if self.friend.alias else self.friend.uid.decode('ascii'))
        self.ui.friendCommentTextEdit.setHtml("""<html><head/><body><p><span style=" color:{};">{}</span></p></body></html>""".format(self.commentColour, self.friend.comment))

    def setAvatar(self):
        # override default avatar if friend has one
        if self.friend.avatar:
            avatar = QtGui.QImage()
            avatar.loadFromData(self.friend.avatar)
            # try fromImage if convert fails
            self.ui.friendAvatarLabel.setPixmap(QtGui.QPixmap.fromImage(avatar))

    def setStatus(self):
        """
        Set stylsheet of the profile's avatar based on status (i.e. Away, Online, Busy, Invisible)
        """
        style = []
        for k, v in ((k.strip(), v.strip()) for k, v in (entry.split(':') for entry in self.ui.friendAvatarLabel.styleSheet().split('\n'))):
            if k == 'border-color':
                rgb, alpha = self.statusColour[self.friend.status]
                v = 'rgba({}, {});'.format(rgb, alpha)

            style.append(': '.join((k, v)))

        self.ui.friendAvatarLabel.setStyleSheet('\n'.join(style))

    def prepareMessage(self):
        msg = self.ui.chatTextEdit.toPlainText()
        if msg:
            rich = self.ui.chatTextEdit.toHtml()

            found = False
            for resource in RESOURCE_PATTERN.findall(rich):
                try:
                    rich = rich.replace(resource, EMOTICON_RESOURCES[resource.split('"')[1]])
                except (KeyError, IndexError):
                    continue
                found = True

            if found:
                self.ui.chatTextEdit.setHtml(rich)
                msg = self.ui.chatTextEdit.toPlainText()

            for emote in EMOTE_PATTERN.findall(msg):
                try:
                    msg = msg.replace(emote, '<img src="{}" />'.format(EMOTICONS[emote]))
                except KeyError:
                    continue

            for url in URL_PATTERN.findall(msg)[1:]:
                msg = msg.replace(url, '<a href="{0}">{0}</a>'.format(url))

            # clear text entry area
            self.ui.chatTextEdit.clear()

            # background the client sending code
            bw = Background(self.sendMessage(msg), loop=self.loop)
            bw.finished.connect(partial(self._displayMessage, msg, bw.workerId))
            bw.start()
            self._background[bw.workerId] = bw

    @asyncio.coroutine
    def sendMessage(self, msg):
        # send the message
        send_message = self.p2pClient.sendMessage(self.friend.uid, msg)
        success = False
        try:
           # success = self.loop.run_until_complete(send_message)
            success = yield from send_message
        except Exceptions.ConnectionFailure:
            # friend may have changed address, contact server for updated details
            details = yield from self.client.getDetails((self.friend.mask,))
            if len(details) > 1:
                # if we have a valid server response, update local details
                self.p2pClient.friends[self.friend.uid] = details[self.friend.mask][1]

                try:
                    # second attempt at message sending
                    success = yield from send_message
                except Exceptions.ConnectionFailure:
                    # friend uncontactable
                    success = False

        if not success:
            # unable to send friend message, ask the server to store it
            yield from self.client.storeMessage(self.friend.mask, msg)

        return success

    def _displayMessage(self, msg, workerId):
        success = self._background[workerId].result
        # delete bw worker holder
        del self._background[workerId]
        if success:
            # add message to history styled by template
            self.ui.historyTextBrowser.append(self.templateOut.format(datetime.now().strftime("%I:%M:%p"),
                                                                      msg.replace('\n', '<br />')))
        else:
            # offline styled text
            self.ui.historyTextBrowser.append(self.templateOff.format(datetime.now().strftime("%I:%M:%p"),
                                                                      msg.replace('\n', '<br />')))


    def receiveMessage(self, message):
        self.ui.historyTextBrowser.append(self.templateIn.format(datetime.now().strftime("%I:%M:%p"),
                                                                 message.replace('\n', '<br />')))

    def emoticonWindow(self):
        if self._emoteWindow is None:
            self._emoteWindow = EmoticonWindow(callback=self.setEmoticon)
        self._emoteWindow.show()
        self._emoteWindow.raise_()

    def setEmoticon(self, emote):
        self.ui.chatTextEdit.insertHtml('<img src="{}" />'.format(EMOTICONS[emote]))
        self.ui.chatTextEdit.moveCursor(QtGui.QTextCursor.End)


class FriendItemDelegate(QtGui.QItemDelegate):
    """
    Specialised items for the FriendsListView
    """
    def __init__(self, friends, parent=None):
        super().__init__(parent)
        self.statusColour = {STATUS_ONLINE: (255, 255, 255, 255),
                             STATUS_AWAY: (255, 170, 0, 50),
                             STATUS_BUSY: (255, 0, 0, 50),
                             STATUS_OFFLINE: (167, 167, 167, 50),
                             STATUS_INVISIBLE: (167, 167, 167, 50)}

        self.size = 52
        self._friends = friends

    def sizeHint(self, *args, **kwargs):
        # override size of items in list
        return QtCore.QSize(self.size, self.size)

    def paint(self, painter, option, index):
        painter.save()

        # set background color base on status
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(*self.statusColour[list(self._friends.values())[index.row()].status])))
        painter.drawRect(option.rect)

        # height separation multiplier
        height = index.row() * self.size

        ##########################################
        # draw avatar and pending messages amount
        ##########################################
        avatar, pending = index.data(QtCore.Qt.DecorationRole)
        #painter.drawImage(QtCore.QRectF(8, 8 + height, 32, 32), avatar)
        painter.drawImage(QtCore.QRectF(8, 8 + height, 32, 32), avatar)

        # pending messages text done in Droid Sans, 10, QtGui.QFont.Bold AND QtGui.QPen(QtCore.Qt.white)
        if pending:
            left = option.rect.width() - 32
            # draw icon, left - top - width - height
            painter.drawImage(QtCore.QRectF(left, 8 + height, 24, 18), QtGui.QImage(":/quip/Images/bubble_24x18.png"))

            # draw pending message number within the icon
            painter.setPen(QtGui.QPen(QtCore.Qt.white))
            painter.setFont(QtGui.QFont("Droid Sans", 8, QtGui.QFont.Bold))
            painter.drawText(QtCore.QRectF(left + (9 if pending < 10 else 6), 11 + height, 10 if pending <= 10 else 20, 18), str(pending))

        ####################
        # draw userId/alias
        ####################
        # set text color
        painter.setPen(QtGui.QPen(QtCore.Qt.black))
        # set font
        painter.setFont(QtGui.QFont("Droid Sans", 10, QtGui.QFont.Normal))
        alias, comment, _ = index.data(QtCore.Qt.DisplayRole)
        #painter.drawText(option.rect, QtCore.Qt.AlignCenter, ", alias)
        painter.drawText(QtCore.QRectF(64, 8 + height, len(alias) * 10, 18), alias)

        #######################
        # Draw partial comment
        #######################
        painter.setFont(QtGui.QFont("Droid Sans", 8, QtGui.QFont.Normal))
        painter.setPen(QtGui.QPen(QtCore.Qt.lightGray))
        painter.drawText(QtCore.QRectF(64, 26 + height, min(len(comment)*5, 300), 14), comment)

        painter.restore()

class FriendListModel(QtCore.QAbstractListModel):
    def __init__(self, friends, pending, parent=None):
        super().__init__(parent)
        self._friends = friends
        self._pending = pending

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled if list(self._friends.values())[index.row()].status not in (STATUS_OFFLINE, STATUS_INVISIBLE) else QtCore.Qt.NoFocus

        return QtCore.Qt.NoFocus | QtCore.Qt.ItemIsEnabled if list(self._friends.values())[index.row()].status not in (STATUS_OFFLINE, STATUS_INVISIBLE) else ''

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return self._friends

    def rowCount(self, parent):
        return len(self._friends)

    def data(self, index, role):
        f = list(self._friends.values())[index.row()]
        if role == QtCore.Qt.DisplayRole:
            return f.alias if f.alias else f.uid.decode('ascii'), f.comment, f.mask

        if role == QtCore.Qt.DecorationRole:
            # return icon with avatar or placeholder
            if f.avatar:
                image = QtGui.QImage()
                image.loadFromData(f.avatar)
            else:
                image = QtGui.QImage(":/quip/Images/default-avatar-64x64.png")

            return image, self._pending[f.uid]

class FriendsList(QtGui.QMainWindow):

    def __init__(self, client, server, p2pClient, loop=None, parent=None):
        """
        FriendsList window contructor

        @param client: Server Client object (logged in)
        @param server: P2P Server object
        @param p2pClient: P2P Client object
        """
        super().__init__(parent)
        self.friends = OrderedDict()
        self.pending = Counter()
        # initial user interface setup
        self.ui = Ui_FriendList()
        self.ui.setupUi(self)
        self.__fileTransferWindow = None
        self.__settingsWindow = None

        # status colour layouts for user. Format is (rgb, alpha)
        self.statusColour = {STATUS_ONLINE: ('255, 255, 255', 100),
                             STATUS_AWAY: ('255, 170, 0', 100),
                             STATUS_BUSY: ('255, 0, 0', 100),
                             STATUS_INVISIBLE: ('167, 167, 167', 100)}

        # current status
        self.status = STATUS_ONLINE

        # server client
        self.client = client
        # p2p client
        self.p2pClient = p2pClient
        # p2p server
        self.server = server
        # asyncio loop
        self.loop = loop or asyncio.get_event_loop()
        # logged in user's profile
        self.profile = self.getProfile()
        # current alias
        self.alias = ''
        self.commentColour = '#8d8d8d'

        # periodic server check for messages and transfers, every 300ms
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.checkServer)
        self.timer.start(300)

        # TODO: replace with UDP heartbeat
        self.ftimer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.getRequests)
        # every 5 seconds
        self.timer.start(5000)

        ######################
        # Additional UI setup
        ######################

        # correctly space out buttons on the toolbar
        self.ui.spacerWidgetLeft = QtGui.QWidget()
        self.ui.spacerWidgetLeft.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.ui.toolBar.insertWidget(self.ui.actionFriendAdd, self.ui.spacerWidgetLeft)
        self.ui.spacerWidgetRight = QtGui.QWidget()
        self.ui.spacerWidgetRight.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.ui.toolBar.insertWidget(self.ui.actionPatron, self.ui.spacerWidgetRight)

        self.setAvatarStatus()
        self.checkPatronStatus()

        # drawing profile first avoids sending avatar to friends as self.friends has not yet been populated
        self.drawProfile()
        self.drawFriendlist()

        ###############
        # Signal setup
        ###############
        self.ui.actionDeleteFriend.triggered.connect(self.deleteFriend)
        self.ui.friendsListView.doubleClicked.connect(self.createChat)
        self.ui.friendsListView.addAction(self.ui.actionDeleteFriend)
        self.ui.actionFriendAdd.triggered.connect(self.profileSearch)
        self.ui.actionSearchProfiles.triggered.connect(self.profileSearch)
        self.ui.actionPatron.triggered.connect(self.openPatronWebsite)
        self.ui.actionSettings.triggered.connect(self.settingsWindow)
        self.ui.actionTransfers.triggered.connect(self.showTransferWindow)
        self.ui.actionQuit.triggered.connect(self.shutdown)
        self.ui.actionInviteCodes.triggered.connect(self.invitesWindow)

        self.ui.actionOnline.triggered.connect(self.setStatus)
        self.ui.actionAway.triggered.connect(self.setStatus)
        self.ui.actionBusy.triggered.connect(self.setStatus)
        self.ui.actionInvisible.triggered.connect(self.setStatus)

        # ensure the focus is originally on avatar
        self.ui.avatarLabel.setFocus()

    def checkPatronStatus(self, refreshProfile=False):
        """
        Checks logged in user's patron status and updates patron star button
        """
        # obtain profile from server
        if refreshProfile:
            self.profile = self.getProfile()

        if (float(self.profile['patron']) - time()) > 0:
            patronIcon = QtGui.QIcon()
            patronIcon.addPixmap(QtGui.QPixmap(":/quip/Images/patron.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.ui.actionPatron.setIcon(patronIcon)


    def closeEvent(self, event):
        self.p2pClient.shutdown()
        self.server.stop(self.loop)
        event.accept()

    def shutdown(self):
        self.close()

    def mouseDoubleClickEvent(self, ev, **kwargs):
        # react to doubleclick in avatar location
        if 3 < ev.x() < 72 and 30 < ev.y() < 120:
            self.profile = self.getProfile()
            self._profileView = ProfileView(self.ui.avatarLabel.pixmap(), self.profile, self.client, self.p2pClient,
                                            self.drawProfile, self.loop)
            self._profileView.show()
        return True

    def deleteFriend(self):
        data = self.ui.friendsListView.currentIndex().data(QtCore.Qt.DisplayRole)
        if data:
            alias, _, mask = data
            confirm = messageBox('warning', "Are you sure you want to delete {}?".format(alias),  confirm=True)

            if confirm == QtGui.QMessageBox.Yes:
                self.loop.run_until_complete(self.client.deleteFriend(mask))
                self.drawFriendlist()

    def setStatus(self):
        """
        Update status of logged in user
        """
        selected = self.sender().text().lower()
        status = [k for k, v in STATUSES_BASIC.items() if v == selected][0]

        success = self.loop.run_until_complete(self.client.setStatus(status))

        if success:
            self.status = status
            self.setAvatarStatus()
        else:
            messageBox('warning', 'Unable to change status, try again later')

    def setAvatarStatus(self):
        """
        Set stylsheet of the profile's avatar based on status (i.e. Away, Online, Busy, Invisible)
        """
        style = []
        for k, v in ((k.strip(), v.strip()) for k, v in (entry.split(':') for entry in self.ui.avatarLabel.styleSheet().split('\n'))):
            if k == 'border-color':
                rgb, alpha = self.statusColour[self.status]
                v = 'rgba({}, {});'.format(rgb, alpha)

            style.append(': '.join((k, v)))

        self.ui.avatarLabel.setStyleSheet('\n'.join(style))

    def getRequests(self):
        """
        Check for friend requests
        """

        try:
            requests = self.loop.run_until_complete(self.client.getRequests())
        except RuntimeError:
            # currently waiting on read()
            requests = None

        if requests:
            try:
                assert self._friendRequestWindow.isVisible() is True
            except (AssertionError, AttributeError):
                self._friendRequestWindow = FriendRequest(self.client, self.p2pClient, self.drawFriendlist, requests,
                                                          loop=self.loop)
                self._friendRequestWindow.show()

    def checkServer(self):
        """
        Check P2P Server for waiting messages or transfer requests
        """
        # send messages to their appropriate chat window
        while True:
            # destructive iterate over message container to ensure all messages are obtained before deletion
            try:
                uid, messages = self.server.messages.popitem()
            except KeyError:
                break

            mask = self.p2pClient.masks[uid]
            try:
                w = getattr(self, mask)
            except AttributeError:
                f = self.friends[uid]
                setattr(self, f.mask, ChatWindow(self.alias, f, self.getProfile(uid), self.p2pClient, self.client,
                                                 self.fileTransferWindow, self.server.fileRequestsOut.reload,
                                                 ignore=[rowid for rowid, message in messages], loop=self.loop))
                w = getattr(self, mask)

            for (rowid, msg) in messages:
                # decode bytes data received by server
                w.receiveMessage(msg.decode('utf-8'))

            if not w.isActiveWindow():
                self.pending[uid] += len(messages)
            else:
                self.pending[uid] = 0

            self.drawFriendlist()

        save = False
        # send auth tokens to server
        for n, token in enumerate(self.server.auth + self.p2pClient.auth):
            success = self.loop.run_until_complete(self.client.addAuthorisationToken(token=token))

            try:
                assert success is True
            except AssertionError:
                # unable to send to server, try again later
                save = True
                break

        if self.server.auth or self.p2pClient.auth or self.server.avatar:
            # redraw friend list
            self.drawFriendlist()
            self.server.avatar = False

        if not save:
            self.server.auth.clear()
            self.p2pClient.auth.clear()

        # incoming file transfer requests
        if len(self.server.fileRequests):
            # bring up file transfer request window
            self.fileTransferWindow(refresh=True)

    def invitesWindow(self):
        """
        Create and show Invites window
        """
        self.__invitesWindow = InviteCodes(self.client, loop=self.loop)
        self.__invitesWindow.show()

    def profileSearch(self):
        """
        Create profile search window
        """
        # profile search window should never require refocus or reuse
        self.__profileSearch = ProfileSearchWindow(self.alias, self.client, loop=self.loop)
        self.__profileSearch.show()

    def openPatronWebsite(self):
        """
        Open Patron URL
        """
        self.checkPatronStatus(refreshProfile=True)
        patronWebsite()

    def settingsWindow(self):
        """
        Create and show settings window
        """
        if self.__settingsWindow is None:
            self.__settingsWindow = SettingsWindow()
        self.__settingsWindow.raise_()
        self.__settingsWindow.show()

    def showTransferWindow(self):
        if self.__fileTransferWindow is None:
            self.__fileTransferWindow = FileTransferWindow(self.p2pClient, self.server, self.friends, loop=self.loop)
        self.__fileTransferWindow.raise_()
        self.__fileTransferWindow.show()

    def fileTransferWindow(self, refresh=True):
        """
        Create/Display file transfer window
        """
        new = False
        toRaise = False
        if self.__fileTransferWindow is None:
            new = True
            toRaise = True

        if refresh and not new:
            toRaise = self.__fileTransferWindow.redraw()

        if toRaise:
            self.p2pClient.fileRequests.reload()
            self.showTransferWindow()

    def createChat(self, *args):
        """
        Create new chat window for designated friend (or bring up current window if open)
        """
        friend = list(self.friends.values())[args[0].row()]

        if self.pending[friend.uid]:
            # reset pending messages counter
            self.pending[friend.uid] = 0
            self.drawFriendlist()

        try:
            # call up friend's chat window if it exists
            w = getattr(self, friend.mask)
            # reopen if it's been closed
            w.show()
            w.raise_()
        except AttributeError:
            # create new chat window for friend
            setattr(self, friend.mask, ChatWindow(self.alias, friend, self.getProfile(friend.uid), self.p2pClient,
                                                  self.client, self.fileTransferWindow, self.server.fileRequests.reload,
                                                  loop=self.loop))
            w = getattr(self, friend.mask)
            w.show()

    def drawFriendlist(self, retry=False):
        # uid-> mask
        masks = getMasks(self.client.safe, self.client.profileId)
        if masks:
            try:
                # attempt bulk friend list information update
                details = self.loop.run_until_complete(self.client.getDetails(tuple(masks.values())))
            except Exceptions.Unauthorised:
                # failure on one or more friends
                if retry:
                    # friend acceptance handling time allowance (3 secs)
                    QtCore.QTimer.singleShot(3000, self.drawFriendlist)
                    return
                else:
                    denied = []
                    details = {}
                    # friend may have removed authorisation rights
                    for mask in masks.values():
                        try:
                            details.update(self.loop.run_until_complete(self.client.getDetails(mask)))
                        except Exceptions.Unauthorised:
                            denied.append(mask)

                    for mask in denied:
                        # delete unauthorised friends
                        self.loop.run_until_complete(self.client.deleteFriend(mask))

                    # only show authorised users in friend list
                    masks = {u: m for u, m in masks.items() if m not in denied}
            except RuntimeError:
                # draw another time
                return

            # mask-> uid
            uids = {v: k for k, v in masks.items()}
            friends = []
            # friends list view to use QAbstractItemModel
            for mask, alias, avatar in getFriends(self.client.safe, self.client.profileId):
                # user profile information
                p = self.getProfile(uids[mask])
                f = Friend(uids[mask], mask, alias or p['alias'], avatar, p['comment'] or 'No comment', details[mask][1])
                friends.append(f)

            self.friends = OrderedDict((f.uid, f) for f in sorted(friends, key=lambda x: (x.status == STATUS_ONLINE, x.alias)))

            for uid in (u for u in self.friends.keys() if u not in self.pending):
                self.pending[uid] = 0

            model = FriendListModel(self.friends, self.pending)
            delegate = FriendItemDelegate(self.friends)

            self.ui.friendsListView.setModel(model)
            self.ui.friendsListView.setItemDelegate(delegate)

    def drawProfile(self):
        """
        Render profile icon, alias and comment information for logged in user
        """
        # logged in profile alias and avatar setup
        self.__avatar, alias = getAvatar(self.client.safe, self.client.profileId)

        # set logged in user's alias
        self.alias = alias if alias else str(self.client.uid)

        # add alias and profile comment to profile view
        self.ui.aliasLineEdit.setText(self.alias)
        self.ui.commentTextEdit.setHtml("""<html><head/><body><p><span style=" color:{};">{}</span></p></body></html>""".format(self.commentColour, self.profile['comment']))

        if self.__avatar:
            # direct byte data must be loaded with loadFromData, not through the contructor's data signature option (uchar)
            avatar = QtGui.QImage()
            avatar.loadFromData(self.__avatar)

            self.ui.avatarLabel.setPixmap(QtGui.QPixmap.fromImage(avatar))

            uids = [u for u, f in self.friends.items() if f.status != STATUS_OFFLINE]
            if uids:
                self.__bw = Background(self.p2pClient.sendAvatar(self.__avatar,
                                                                 [u for u, f in self.friends.items() if f.status != STATUS_OFFLINE]))
                self.__bw.start()

    def getProfile(self, userId=None):
        """
        Return profile information of given user ID

        @param userId: User ID to obtain profile for. None returns logged in user's profile.
        @return: dictionary object containing profile fields and values
        """
        profile = self.loop.run_until_complete(self.client.getProfile(userId if userId else self.client.uid))

        return profile

class InviteCodes(QtGui.QMainWindow):
    """
    Invite Codes Window
    """
    def __init__(self, client, loop=None, parent=None):
        super().__init__(parent)
        self.ui = Ui_Invites()
        self.ui.setupUi(self)

        # quip server client
        self.client = client

        # asyncio loop
        self.loop = loop or asyncio.get_event_loop()

        # windows defaults
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # connect slots and signals
        self.ui.generateButton.clicked.connect(self.generateInvite)
        self.ui.clearButton.clicked.connect(self.clearInvites)

        # invite icons
        self.icons = {-1: QtGui.QIcon(QtGui.QPixmap(":/quip/Images/invite_expired-16x16.png")),
                      0: QtGui.QIcon(QtGui.QPixmap(":/quip/Images/invite_unclaimed-16x16.png")),
                      1: QtGui.QIcon(QtGui.QPixmap(":/quip/Images/invite_claimed-16x16.png"))}

        self.ui.invitesDescription.setFocus()

        # populate listview with current invite codes
        self.populateInvites()


    def populateInvites(self):
        """
        Obtain invites from server and render in list view
        """
        items = False
        model = QtGui.QStandardItemModel(self.ui.invitesListView)

        remaining, codes = self.loop.run_until_complete(self.client.getInvites())

        for code, status in sorted(codes.items(), key=lambda x: x[1]):
            item = QtGui.QStandardItem(self.icons[status], code)
            # insert new code at the top
            model.insertRow(0, item)
            items = True

        if items:
            self.ui.invitesListView.setModel(model)
            self.ui.invitesListView.show()

        # change remaining invites available label
        self.ui.availableLabel.setText(' '.join(self.ui.availableLabel.text().split()[:-1] + [str(remaining)]))

    def clearInvites(self):
        """
        Clear expired and claimed invites from cache
        """
        self.loop.run_until_complete(self.client.clearInvites())
        if self.ui.invitesListView.model():
            self.ui.invitesListView.model().clear()
        self.populateInvites()

    def generateInvite(self):
        """
        Request invite code from server
        """
        remaining, code = self.loop.run_until_complete(self.client.generateInvite())

        if code:
            self.ui.invitesListView.model().clear()
            self.populateInvites()


class AccountRecovery(QtGui.QMainWindow):
    """
    Account Recovery Window
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_AccountRecovery()
        self.ui.setupUi(self)

        # server-client interaction objects
        self.client = ServerClient()
        # background worker
        self.background = None
        # recovery code storage
        self.code = None

        # set defaults
        self.ui.emailProgressBar.hide()
        self.ui.recoveryProgressBar.hide()
        self.ui.phraseProgressBar.hide()
        # set focus
        self.ui.unlockLabel.setFocus()

        # cleanup on close
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # connect slots and signals
        self.ui.nextButton.clicked.connect(self.emailPage)
        self.ui.recoveryButton.clicked.connect(self.submitCode)
        self.ui.phraseButton.clicked.connect(self.submitPhrase)
        self.ui.emailLineEdit.selectionChanged.connect(self.reset)
        self.ui.recoveryCodeLineEdit.selectionChanged.connect(self.reset)
        self.ui.passphraseLineEdit.selectionChanged.connect(self.reset)
        self.ui.helpButton.clicked.connect(partial(messageBox, 'info', 'Recovery code(s) are sent to the entered email account'))

        # original text and style
        self.origStyleEmail = self.ui.emailLineEdit.styleSheet()
        self.origTextEmail = self.ui.emailLineEdit.placeholderText()
        self.origStyleCode = self.ui.recoveryCodeLineEdit.styleSheet()
        self.origTextCode = self.ui.recoveryCodeLineEdit.placeholderText()
        self.origStylePhrase = self.ui.passphraseLineEdit.styleSheet()
        self.origTextPhrase = self.ui.passphraseLineEdit.placeholderText()

    def closeEvent(self, event):
        """
        Create login screen on close
        """
        self._ = LoginWindow()
        self._.show()

        self.close()

    def reset(self):
        """
        Reset stylesheets and placeholder text for line edits
        """
        if self.ui.emailLineEdit.placeholderText() != self.origTextEmail:
            self.ui.emailLineEdit.setStyleSheet(self.origStyleEmail)
            self.ui.emailLineEdit.setPlaceholderText(self.origTextEmail)

        if self.ui.recoveryCodeLineEdit.placeholderText() != self.origTextCode:
            self.ui.recoveryCodeLineEdit.setStyleSheet(self.origStyleCode)
            self.ui.recoveryCodeLineEdit.setPlaceholderText(self.origTextCode)

        if self.ui.passphraseLineEdit.placeholderText() != self.origTextPhrase:
            self.ui.passphraseLineEdit.setStyleSheet(self.origStylePhrase)
            self.ui.passphraseLineEdit.setPlaceholderText(self.origTextPhrase)

    def submitEmail(self, email):
        """
        Request recovery code

        @param email: email address to submit
        """
        if email:
            # create new account
            self.background = Background(self.client.emailRecovery(email))
            # change to Recovery / code page when completed
            self.background.finished.connect(partial(self.ui.stackedWidget.setCurrentIndex, 1))
            self.background.start()

            # show progress bar
            self.ui.emailProgressBar.show()
            # disable Next button
            self.ui.nextButton.setDisabled(True)

    def emailPage(self):
        """
        Accept email input
        """
        email = self.ui.emailLineEdit.text().strip()
        # check for entered e-mail
        if email:
            # validate email
            if emailValidation(email):
                # send request to server, submitEmail handles showing next page
                self.submitEmail(email)
            else:
                self.ui.emailLineEdit.setText("")
                self.ui.emailLineEdit.setPlaceholderText("Invalid e-mail address")
                self.ui.emailLineEdit.setStyleSheet("background-color: rgba(225, 33, 33, 100);")
                self.ui.unlockLabel.setFocus()
        else:
            # no email entered, bring up recovery page
            self.ui.stackedWidget.setCurrentIndex(1)
            self.ui.recoveryCodeLabel.setFocus()

    def submitCode(self):
        """
        Submit recovery code
        """
        code = self.ui.recoveryCodeLineEdit.text().strip()
        if isValidUUID(code):
            self.code = code
            # go to phrase page
            self.ui.stackedWidget.setCurrentIndex(2)
        else:
            self.ui.recoveryCodeLineEdit.setText("")
            self.ui.recoveryCodeLineEdit.setPlaceholderText("Invalid recovery code")
            self.ui.recoveryCodeLineEdit.setStyleSheet("background-color: rgba(225, 33, 33, 100);")
            self.ui.helpButton.setFocus()

    def submitPhrase(self):
        """
        Submit account phrase
        """
        if 32 > len(self.ui.passphraseLineEdit.text()) < 8:
            self.ui.passphraseLineEdit.setText("")
            self.ui.passphraseLineEdit.setPlaceholderText("Passphrase must be at least 8 characters long")
            self.ui.passphraseLineEdit.setStyleSheet("background-color: rgba(225, 33, 33, 100);")
            self.ui.passphraseIconLabel.setFocus()
        else:
            # attempt account recovery
            self.background = Background(self.client.accountRecovery(self.code, self.ui.passphraseLineEdit.text()))
            self.background.finished.connect(self.recoveryResponse)
            self.background.start()

            # show progress bar
            self.ui.phraseProgressBar.show()
            # disable Recover button
            self.ui.phraseButton.setDisabled(True)

    def recoveryResponse(self):
        """
        Handle client account recovery response
        """
        # check recovery response
        if self.background.result:
            messageBox('info', 'Account recovery successful!')
        else:
            messageBox('error', 'Invalid recovery code')

        self.close()


class NewAccount(QtGui.QMainWindow):
    """
    New Account Creation Form
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =  Ui_NewAccount()
        self.ui.setupUi(self)
        # cleanup on close
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.ui.progressBar.hide()
        self.background = None
        # set defaults
        self.ui.createAccountFailedLabel.hide()

        # connect slots and signals
        self.ui.createAccountButton.clicked.connect(self.createAccount)
        self.ui.passphraseLineEdit.selectionChanged.connect(self.reset)
        self.ui.passphraseLineEdit.returnPressed.connect(self.createAccount)
        self.ui.emailLineEdit.selectionChanged.connect(self.reset)

        # whether to open login screen when window closes
        self.openLogin = True

        self.origStylePhrase = self.ui.passphraseLineEdit.styleSheet()
        self.origTextPhrase = self.ui.passphraseLineEdit.placeholderText()
        self.origStyleEmail = self.ui.emailLineEdit.styleSheet()
        self.origTextEmail = self.ui.emailLineEdit.placeholderText()

    def closeEvent(self, event):
        """
        Create login screen on close
        """
        if self.openLogin:
            self._ = LoginWindow()
            self._.show()

        self.close()

    def reset(self):
        """
        Reset passphrase/email placeholder text and stylesheet
        """
        if self.ui.passphraseLineEdit.placeholderText() != self.origTextPhrase:
            self.ui.passphraseLineEdit.setStyleSheet(self.origStylePhrase)
            self.ui.passphraseLineEdit.setPlaceholderText(self.origTextPhrase)

        if self.ui.emailLineEdit.placeholderText() != self.origTextEmail:
            self.ui.emailLineEdit.setStyleSheet(self.origStyleEmail)
            self.ui.emailLineEdit.setPlaceholderText(self.origTextEmail)

    def createAccount(self):
        """
        Create new account locally and remotely
        """
        if 32 > len(self.ui.passphraseLineEdit.text()) < 8:
            self.ui.passphraseLineEdit.setText("")
            self.ui.passphraseLineEdit.setPlaceholderText("Passphrase must be at least 8 characters long")
            self.ui.passphraseLineEdit.setStyleSheet("background-color: rgba(225, 33, 33, 100);")
            self.ui.commentLineEdit.setFocus()
        elif len(self.ui.emailLineEdit.text().strip()) and not emailValidation(self.ui.emailLineEdit.text().strip()):
            self.reset()
            # entered email is invalid
            self.ui.emailLineEdit.setText("")
            self.ui.emailLineEdit.setPlaceholderText("Invalid e-mail address")
            self.ui.emailLineEdit.setStyleSheet("background-color: rgba(225, 33, 33, 100);")
            self.ui.commentLineEdit.setFocus()
        else:
            self.reset()

            # hide error label
            self.ui.createAccountFailedLabel.hide()
            # create new account
            client = ServerClient()
            self.background = Background(client.createAccount(self.ui.passphraseLineEdit.text(), self.ui.aliasLineEdit.text(), self.ui.codeLineEdit.text()))
            self.background.finished.connect(self._login)
            self.background.start()

            self.ui.createAccountButton.setDisabled(True)
            self.ui.progressBar.show()

    def _login(self):
        """
        Login using background worker thread
        """
        # required profiled id returned from createAccount() background thread
        try:
            profileId, reason = self.background.result[0:4:3]
        except TypeError:
            profileId = None
            reason = "Unable to create account. Try again soon"

        if profileId is None:
            self.ui.progressBar.hide()
            self.ui.createAccountButton.setDisabled(False)
            self.ui.createAccountFailedLabel.setText(reason)
            self.ui.createAccountFailedLabel.show()
            return False

        self.background = Background(signIn, arguments=[profileId, self.ui.passphraseLineEdit.text()], isFuture=False)
        self.background.finished.connect(self._loginFinished)
        self.background.start()

    def _loginFinished(self):
        """
        Post login processing function

        Brings up FriendList on login success, defaults to Login screen on login failure
        """
        self.ui.progressBar.hide()
        self.ui.createAccountButton.setDisabled(False)

        try:
            client, server, p2pClient, reason, loop = self.background.result
        except (TypeError, ValueError):
            # account created, unable to start local services, default to login screen
            self.close()
            return

        if not reason:
            # set profile information
            updateRemoteProfile(self.ui, client, loop=loop)

            self.openLogin = False
            # bring up friendList
            self._ = FriendsList(client, server, p2pClient, loop=loop)
            self._.show()

        self.close()


class LoginWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =  Ui_Login()
        self.ui.setupUi(self)
        # cleanup on close
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # ensure progress bar is not shown
        self.ui.progressBar.hide()
        self.background = None

        # defaults
        self.ui.failedLoginLabel.hide()
        self.ui.recoveryButton.hide()

        # connect slots and signals
        self.ui.phraseInput.returnPressed.connect(self.login)
        self.ui.loginButton.clicked.connect(self.login)
        self.ui.recoveryButton.clicked.connect(self.recovery)
        self.ui.newAccountButton.clicked.connect(self.newAccount)

        # load up current profiles from the database
        self.ui.profileComboBox.addItems(['        '.join((str(r), a)) for r, a in getProfiles()])

        # only keep background style for the initial box
        for n in range(self.ui.profileComboBox.count()):
            self.ui.profileComboBox.setItemData(n + 1, QtGui.QColor(QtCore.Qt.white), QtCore.Qt.BackgroundRole)

    def _unfade(self):
        if self.windowOpacity() < 0.55:
            self.setWindowOpacity(1)
            QtCore.QTimer.singleShot(50, self.blink)
        else:
            self.setWindowOpacity(1)

    def blink(self, repeat=False):
        if not repeat:
            self.setWindowOpacity(0.6)
        else:
            self.setWindowOpacity(0.5)

        QtCore.QTimer.singleShot(200, self._unfade)

    def newAccount(self):
        # bring up new account wizard
        self._ = NewAccount()
        self._.show()

        self.close()

    def recovery(self):
        # bring up account recovery window
        self._ = AccountRecovery()
        self._.show()

        self.close()

    def login(self):
        # check profile selected and passphrase entered
        if self.ui.phraseInput.text() == '' or self.ui.profileComboBox.currentText() in ('Select Profile...', ''):
            self.blink(True)
        else:
            self.background = Background(signIn,
                                         arguments=[self.ui.profileComboBox.currentText().split(' ')[0],
                                                    self.ui.phraseInput.text()],
                                         isFuture=False)
            self.background.finished.connect(self._loginFinished)
            self.background.start()

            # disable UI input options and show progress bar
            self.ui.profileComboBox.hide()
            self.ui.phraseInput.hide()
            self.ui.loginButton.setDisabled(True)
            self.ui.newAccountButton.setDisabled(True)
            self.ui.progressBar.show()

    def _loginFinished(self):
        # renable input options and hide progress bar
        self.ui.progressBar.hide()
        self.ui.profileComboBox.show()
        self.ui.phraseInput.show()
        self.ui.loginButton.setDisabled(False)
        self.ui.newAccountButton.setDisabled(False)

        try:
            client, server, p2pClient, reason, loop = self.background.result
        except (TypeError, ValueError):
            error = type(self.background.result)
            if error is ConnectionRefusedError:
                self.ui.failedLoginLabel.setText("Quip server temporarily unavailable")
            elif error is ConnectionError:
                self.ui.failedLoginLabel.setText("Check internet connection")
            else:
                # unable to bind socket
                self.ui.failedLoginLabel.setText("Unable to start server, try again soon")

            self.ui.failedLoginLabel.show()
            return True

        if not reason:
            # bring up friendList
            self._ = FriendsList(client, server, p2pClient, loop=loop)
            self._.show()
            # get rid of this screen
            self.close()
        else:
            logging.info("Failed login, reason: {}".format(reason))
            # unable to create account
            self.ui.failedLoginLabel.setText("Login Failed")
            self.ui.failedLoginLabel.show()
            self.ui.recoveryButton.show()


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)

    app = QtGui.QApplication(sys.argv)
    if checkCerts():
        mySW = LoginWindow()
        mySW.show()
        sys.exit(app.exec_())
    else:
        messageBox('error', "Unable to find or create encryption certificates. Check 'Resources' directory")
        app.quit()
        sys.exit(-1)