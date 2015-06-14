#
# Response handlers for P2P Server
#

import asyncio
import logging
from functools import partial
from hashlib import sha1, sha384
from uuid import uuid4
from os import path

from lib.Database import getFriendRequests, getSigningKeys, setUidMask, storeAuthority, setFriendAuth, getMessageKeys, \
    setAddress, getFileRequests, storeFileRequest, delFileRequests, delFriendRequests, getFriendChecksum, \
    updateFriendDetails, storeHistory
from lib.Utils import isValidUUID, sha1sum
from lib.Constants import BTRUE, BFALSE, WRITE_END, COMMAND_LENGTH, NONEXISTANT, PROFILE_VALUE_SEPARATOR, \
    LIMIT_AVATAR_SIZE, MODIFIED_FILE

######################################
# Server Dispatch Coroutine Handlers
######################################

@asyncio.coroutine
def friendAcceptance(reader, writer, safe, profileId, data, requests=None):
    """
    Handle incoming friend request acceptance (P2P)

    Once a request has been made, and the destination user accepts, the destination user contacts the request user
    who runs this coroutine to complete the friendship.

    Requester->Server (quip client, friendRequest)
    Server->Destination (Heartbeat token)
    Destination->Server (quip client, getRequests)
    Destination->Requester (p2p client, friendCompletion) to (p2p server, this coroutine)

    @param reader: StreamReader object
    @param writer: StreamWriter objet
    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @param data: uid followed by hash of message
    @param requests: (Optional) Recent outgoing friend requests {uid: message hash}
    @return: Auth token
    """
    if not requests:
        requests = {}

    # auth token
    auth = None
    try:
        # verify required input data length
        assert len(data) == 76
        # user id, message hash
        mhash, uid = data[:-36], data[-36:]
        # valid UUID
        assert isValidUUID(uid) is True
    except AssertionError:
        logging.info("\t".join(("Invalid friend completion data received", "Data: {!r}".format(data))))
        return b''.join((BFALSE, WRITE_END)), auth

    if uid not in requests:
        # check db for older requests
        requests.update(getFriendRequests(safe, profileId))

    # obtain request information for this user (uid)
    try:
        msg, timestamp, _, rowid = requests[uid]
    except KeyError:
        logging.warning("\t".join(("Friend Request Failure",
                                   "No friend request found for given user ID", "UID: {!r}".format(uid))))
        return b''.join((BFALSE, WRITE_END)), auth

    # ensure our potential friend has the correct hash value for the friend request
    try:
        assert mhash.decode('ascii') == sha1(b''.join((uid, msg))).hexdigest()
    except (UnicodeDecodeError, AssertionError):
        logging.warning("\t".join(("Friend Request Failure", "Hash values do not match",
                                   "Sent: {!r}".format(mhash),
                                   "Local: {!r}".format(sha1(b''.join((uid, msg))).hexdigest()))))
        return b''.join((BFALSE, WRITE_END)), auth

    # hash value has matched, get public key
    spub = getSigningKeys(safe, profileId)[1]
    mpub = getMessageKeys(safe, profileId)[1]

    # auth token sent to friend
    token = bytes(str(uuid4()), encoding='ascii')
    # create our auth token to be sent to server
    auth = bytes(sha384(b''.join((uid, token))).hexdigest(), encoding='ascii')


    # work out length of data
    data = b''.join((token, spub, mpub))
    # send length to read and auth token and public keys
    writer.write(b''.join((bytes(str(len(data)), encoding='ascii'), WRITE_END, data)))
    yield from writer.drain()

    # recv back success to confirm storage of sent data by friend
    success = yield from reader.readline()
    try:
        assert int(success[0]) == 49
        int(success)
    except (KeyError, ValueError):
        logging.warning("\t".join(("Friend Request Warning",
                                   "Friendship completion failed. Storage confirmation: {!r}".format(success))))
        return b''.join((BFALSE, WRITE_END)), None

    port = success[1:-1]
    # receive length to read
    data = yield from reader.readline()
    try:
        length = int(data)
    except ValueError:
        return b''.join((BFALSE, WRITE_END)), None

    data = yield from reader.read(length)

    fauth, spub, mpub = data[:36], data[36:100], data[100:]

    try:
        assert len(data) > 115
        assert isValidUUID(fauth) is True
    except AssertionError:
        logging.error("\t".join(("Friend Request Failure",
                                 "Invalid mask or public key provided", "Data: {!r}".format(data))))
        return b''.join((BFALSE, WRITE_END)), None

    # created and store localised mask of friend's true ID
    fmask = setUidMask(safe, profileId, uid)

    # store friend's auth mask
    # (the mask we use when submitting authorised requests to the hub server regarding this friend)
    setFriendAuth(safe, profileId, fmask, fauth, auth)

    # store public key for friend
    storeAuthority(safe, profileId, fmask, spub, mpub)

    # store address locally
    setAddress(safe, profileId, fmask,
               b':'.join((bytes(writer.transport.get_extra_info('peername')[0], encoding='ascii'), port)))

    # delete local friend request storage
    delFriendRequests(rowid)

    # True for success of all required friendship steps, hash of auth token we sent to friend (must be sent to hub server)
    return BTRUE, auth

@asyncio.coroutine
def requestSendFile(safe, profileId, mask, data):
    """
    Handle and store request for file transfer

    @param safe: crypto box
    @param profileId: logged in user's profile ID
    @param mask: local friend mask for given friend's user ID
    @param data: filename, size, checksum seperated by VALUE_SEPERATOR and user ID
    @return: user id, filename, size
    """
    try:
        filename, size, checksum = data[:-36].split(bytes(PROFILE_VALUE_SEPARATOR, encoding='utf-8'))
    except ValueError:
        logging.info("Invalid file request data recieved: {!r}".format(data))
        return False

    checksum = checksum[:-COMMAND_LENGTH]
    # validate received data
    try:
        # sha1 hex length
        assert len(checksum) == 40
        # size in bytes must be integer
        int(size)
    except AssertionError:
        logging.info("Invalid file request data received, checksum is not correct length: {!r}".format(checksum))
        return False
    except ValueError:
        logging.info("Invalid file request data received, size is not an integer: {!r}".format(size))
        return False

    # store file transfer request
    rowid = storeFileRequest(safe, profileId, outgoing=False, mask=mask, request=(filename, size, checksum))

    return data[-36:], filename, size, checksum, rowid

@asyncio.coroutine
def sendFile(writer, safe, profileId, mask, checksum, expiry, blockSize=4098):
    """
    Send file to from server to client destination

    @param writer: StreamWriter object to client
    @param safe: crypto box
    @param profileId: logged in user's profile ID
    @param mask: local friend mask for given friend's user ID
    @param checksum: sha1 sum value of file to be sent
    @param expiry: expire days for file transfer requests (config set value)
    @param blockSize: total number of bytes to read at once
    @return: True when file if completely sent, otherwise False
    """
    try:
        # obtain current requests for provided mask and clear expired requests
        filename, size, rowid = getFileRequests(safe, profileId, outgoing=True, mask=mask, expire=expiry)[mask][checksum]
    except KeyError:
        logging.warning("\t".join(("File Transfer Failed",
                                   "File transfer request does not exist for mask {} and checksum {}".format(mask, checksum))))
        writer.write(NONEXISTANT)
        yield from writer.drain()
        return False

    if not path.isfile(filename):
        delFileRequests(rowid)
        logging.warning("\t".join(("File Transfer Failed", "File no longer exists: {}".format(filename))))
        writer.write(NONEXISTANT)
        yield from writer.drain()
        return False

    # match file checksum to ensure the same file which was to be sent
    # has not been modified since the original transfer request
    cursum = sha1sum(filename)
    if checksum != cursum:
        # remove invalid transfer request
        delFileRequests(rowid)
        logging.warning("\t".join(("File Transfer Failed", "File has been modified",
                                   "Filename: {}".format(filename),
                                   "Original checksum: {}".format(checksum),
                                   "Current checksum: {}".format(cursum))))
        writer.write(MODIFIED_FILE)
        yield from writer.drain()

        return False

    blockSize = int(blockSize)
    with open(filename, 'rb') as fd:
        for buf in iter(partial(fd.read, blockSize), b''):
            writer.write(buf)

        yield from writer.drain()

    # remove file transfer request from storage
    delFileRequests(rowid)

    return True

@asyncio.coroutine
def receiveAvatar(reader, writer, safe, profileId, mask, checksum):
    """
    Receive avatar update check from friend

    @param reader: client streamreader object
    @param writer: streamwriter object
    @param safe: crypto box
    @param profileId: logged in user's profile ID
    @param mask: friend mask uid
    @param checksum: avatar sha1 checksum
    @return: '0' if avatar not updated, otherwise locally calculated checksum value of stored avatar
    """
    if len(checksum) != 40:
        logging.warning("Friend mask '{}' tried to send invalid checksum value: {!r}".format(mask, checksum))
        return BFALSE

    try:
        checksum = checksum.decode('ascii')
    except UnicodeDecodeError:
        return BFALSE

    # compare local checksum value
    if checksum != getFriendChecksum(safe, profileId, mask):
        writer.write(BTRUE)
        yield from writer.drain()
    else:
        return BFALSE

    # get size of avatar to read from friend
    size = yield from reader.readline()

    try:
        size = int(size)
        assert size < LIMIT_AVATAR_SIZE
    except (ValueError, AssertionError):
        logging.warning("Friend mask '{}' tried to send invalid avatar size value: {!r}".format(mask, size))
        return BFALSE

    writer.write(BTRUE)
    yield from writer.drain()

    # read avatar into memory
    avatar = yield from reader.readexactly(size)

    # store avatar
    storedChecksum = updateFriendDetails(safe, profileId, mask, avatar=avatar)

    # send locally calculated checksum value as verification of storage
    return storedChecksum

@asyncio.coroutine
def receiveMessage(safe, profileId, mask, data):
    """
    Process data as recieved message

    @param data: bytes/bytestring of msg and uid sent by client
    @return: (user id, received message) if receive message exists, else False
    """
    # msg portion of data
    msg = data[:-36 - COMMAND_LENGTH]

    rowid = storeHistory(safe, profileId, mask, msg, fromFriend=True)
    # uid, msg
    return (rowid, data[-36:], msg) if msg else False

#######################
# P2P Client Handlers
#######################

@asyncio.coroutine
def inviteChat():
    pass
