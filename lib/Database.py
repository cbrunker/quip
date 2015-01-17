#
# Quip Client database handling
#

# built-ins
from collections import defaultdict
import logging
from datetime import datetime
from sqlite3 import connect, IntegrityError
from uuid import uuid4
from os import path
from hashlib import sha1

# third party
from nacl.exceptions import CryptoError
from nacl.public import PrivateKey
import nacl.signing
import nacl.encoding
import nacl.utils
from nacl.secret import SecretBox

# application modules
from lib.Utils import encrypt, absolutePath


def getCursor(location=path.join('Resources', 'quip.db')):
    """

    @param location: file location of database
    @return: database connection cursor
    """
    return connect(absolutePath(location), isolation_level=None).cursor()

def getAddress(safe, profileId, mask):
    """
    Return IP and Port for provided uid

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @param mask: friend's user ID mask
    @return: last known (ip, port)
    """
    con = getCursor()
    con.execute("SELECT address FROM address WHERE profile_id=? AND friend_mask=?", (profileId, mask))
    out = con.fetchone() or ()

    return safe.decrypt(out[0]) if out is not None else out

def setAddress(safe, profileId, mask, addr):
    """
    Set address associated with masked friend ID

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @param mask: friend's uid mask
    @param addr: address in form socket type:ip:port
    """
    con = getCursor()
    con.execute("INSERT INTO address (profile_id, friend_mask, address) VALUES (?, ?, ?)",
                [profileId, mask] + list(encrypt(safe, addr)))

def updateAddress(safe, profileId, mask, addr):
    """
    Update address associated with masked friend ID

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @param mask: friend's uid mask
    @param addr: address in form of socket type:ip:port
    """
    con = getCursor()
    con.execute("SELECT count(profile_id) FROM address where profile_id=? and friend_mask=?", (profileId, mask))
    if int(con.fetchone()[0]):
        con.execute("UPDATE address SET address=? WHERE profile_id=? AND friend_mask=?",
                    list(encrypt(safe, addr)) +[profileId, mask])
    else:
        setAddress(safe, profileId, mask, addr)

def getAuthority(safe, profileId, mask):
    """
    Return public key for given friend (mask)

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @param mask: localised mask of friend's ID
    @return: (signing public key, encryption public key)
    """
    con = getCursor()
    con.execute("SELECT verify_key, public_key FROM friends WHERE profile_id=? AND friend_mask=?", (profileId, mask))
    out = con.fetchone() or ()

    return tuple(safe.decrypt(i) for i in out)

def storeAuthority(safe, profileId, mask, signingKey, messageKey):
    """
    Store new public key for uid (friend).

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @param mask: localised mask of friend's ID
    @param signingKey: friend's digital signature public key
    @param messageKey: friend's message encryption public key
    @return: True if successfully set, otherwise False if entry currently exists
    """
    con = getCursor()

    # try to insert new entry
    try:
        con.execute("INSERT INTO friends (profile_id, friend_mask, verify_key, public_key) VALUES (?, ?, ?, ?)",
                    [profileId, mask] + list(encrypt(safe, signingKey, messageKey)))
        success = True
    except IntegrityError:
        # friend entry already exists
        logging.error("Authority Error", "Trying to override current friends public key")
        success = False

    return success

def getFriends(safe, profileId):
    """

    @return:
    """
    con = getCursor()

    con.execute("SELECT friend_mask, alias, avatar FROM friends WHERE profile_id=?", (profileId,))
    out = con.fetchall() or ()

    return tuple((out[0], safe.decrypt(out[1]) if out[1] else b'', safe.decrypt(out[2]) if out[2] else b'') for out in out)

def getProfiles():
    con = getCursor()
    con.execute("SELECT ROWID, alias FROM profiles")

    return con.fetchall()

def getLocalAuth(profileId, phrase):
    """
    Return complete authorisation phrase for provided profile

    @param profileId: profile ID
    @param phrase: partial passphrase
    @return: 32 byte auth phrase as bytes object, False if profileId does not exist
    """
    if len(phrase) < 32:
        con = getCursor()

        con.execute("SELECT buffer FROM profiles WHERE ROWID=?", (profileId,))
        out = con.fetchone()
        if not out:
            return False

        phrase = b''.join((bytes(phrase, encoding='utf-8'), out[0][len(phrase) - 32:]))
    else:
        phrase = bytes(phrase[:32], encoding='utf-8')

    return phrase

def storeAccount(phrase, uid, auth, alias):
    """
    Store new account information

    @param phrase: new passphrase as bytes
    @param uid: user id
    @param auth: authentication token
    @param alias: user set alias for profile
    @return: Profile ID of newly created profile and safe
    """
    con = getCursor()

    # random phrase buffer
    buffer = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    # create safe (db encryption)
    safe = SecretBox(b''.join((phrase, buffer[len(phrase) - 32:])))
    # create new signing_key and verify_key (message signing)
    skey = nacl.signing.SigningKey.generate()
    # create new private and public key (message encryption)
    mkey = PrivateKey.generate()

    con.execute("INSERT INTO profiles (uid, auth, signing_key, verify_key, private_key, public_key, buffer, alias) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                list(encrypt(safe, uid, auth, skey._seed, skey.verify_key.encode(encoder=nacl.encoding.HexEncoder),
                             mkey._private_key, mkey.public_key._public_key)) + [buffer, alias])

    profileId = con.lastrowid

    return profileId, safe

def updateAccount(safe, profileId, auth):
    """
    Update profile information with new auth token

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @param auth: Authentication token
    """
    con = getCursor()
    con.execute("UPDATE profiles SET auth=? WHERE ROWID=?", list(encrypt(safe, auth)) + [profileId])

def getAccount(safe, profileId):
    """
    Return profile information

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @return: (uid, pid) if profile exists, else None, None
    """
    con = getCursor()
    con.execute("SELECT uid, auth FROM profiles WHERE ROWID=?", (profileId,))
    out = con.fetchone() or ()

    try:
        return tuple(safe.decrypt(i) for i in out)
    except CryptoError:
        return None, None

def setAvatar(safe, profileId, avatar):
    """
    Set a new avatar for given profile

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @param avatar: avatar data to store. If str object, avatar will be taken as a path to a file, otherwise byte data assumed
    """
    con = getCursor()
    con.execute("UPDATE profiles SET avatar=? WHERE ROWID=?", list(encrypt(safe, avatar)) + [profileId])

def getAvatar(safe, profileId):
    """
    Return avatar and alias details for given profile

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @return: avatar data as bytes, user set alias as string
    """
    con = getCursor()
    con.execute("SELECT avatar, alias FROM profiles WHERE ROWID=?", (profileId,))

    out = con.fetchone() or ()

    return safe.decrypt(out[0]) if out[0] else out[0], out[1]

def updateFriendDetails(safe, profileId, mask, avatar=None, alias=None):
    """
    Set localiased friend details (avatar and alias).

    NOTE: setting avatar evaluates and sets new checksum value

    @param safe: crypto box
    @param profileId: logged in profile ID
    @param mask: friend's local (masked) user ID
    @param avatar: friend's avatar data
    @param alias: friend's alias
    @return: (Boolean) Success of update if avatar is None, else checksum value
    """
    if avatar is None and alias is None:
        return False

    checksum = None
    con = getCursor()
    if avatar:
        checksum = bytes(sha1(avatar).hexdigest(), encoding='ascii')
        con.execute("UPDATE friends SET checksum=?, avatar=? WHERE profile_id=? AND friend_mask=?",
                    list(encrypt(safe, checksum, avatar)) + [profileId, mask])

    if alias:
        con.execute("UPDATE friends SET alias=? WHERE profile_id=? AND friend_mask=?",
                    list(encrypt(safe, alias)) + [profileId, mask])

    return checksum or True

def getFriendDetails(safe, profileId, mask):
    """
    Return friend's avatar and alias

    @param safe: crypto box
    @param profileId: logged in user's profile ID
    @param mask: friend mask
    @return: avatar, alias
    """
    con = getCursor()
    con.execute("SELECT avatar, alias from friends WHERE profile_id=? AND friend_mask=?", (profileId, mask))
    out = con.fetchone() or ()

    return tuple(safe.decrypt(i) if i else i for i in out)

def getFriendChecksum(safe, profileId, mask):
    """
    Return friend's avatar checksum value

    @param safe: crypto box
    @param profileId: logged in user's profile ID
    @param mask: friend mask
    @return: checksum value of avatar, '' if no avatar set for friend
    """
    con = getCursor()
    con.execute("SELECT checksum FROM friends WHERE profile_id=? AND friend_mask=?", (profileId, mask))
    out = con.fetchone()

    return safe.decrypt(out[0]) if len(out) == 1 and out[0] else ''

def deleteFriend(safe, profileId, mask):
    """
    Delete stored data for given friend mask.

    NOTE: This is local storage deletion, client should ensure to delete authorisation token for friend on main server

    @param safe: crypto box
    @param profileId: logged in profile id
    @param mask: friend's ID mask
    @return: True if successfully deleted, otherwise False
    """
    # sanity check on uid
    con = getCursor()
    con.execute("SELECT friend_uid FROM friend_mask WHERE profile_id=? AND friend_mask=?", (profileId, mask))

    try:
        safe.decrypt(con.fetchone()[0])
    except Exception:
        return False

    for table in  ('address', 'history', 'file_requests', 'friend_auth', 'friend_mask', 'friends'):
        con.execute("DELETE FROM {} WHERE profile_id=? AND friend_mask=?".format(table), (profileId, mask))

    return True

def deleteAccount(safe, profileId, uid):
    """
    Delete profile and all associated data (history, friends, auth tokens, requests, addresses)

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @param uid: logged in User ID
    @return: True if successfully deleted, otherwise False
    """
    if uid == getAccount(safe, profileId)[0]:
        con = getCursor()
        for table in ('history', 'file_requests', 'address', 'friend_auth', 'friends', 'friend_mask'):
            con.execute("DELETE FROM {} WHERE profile_id=?".format(table), (profileId,))

        con.execute("DELETE FROM profiles WHERE ROWID=?", (profileId,))
        return True

    return False

def getSigningKeys(safe, profileId):
    """
    Return private and public keys for given profile ID

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @return: (private key, public key)
    """
    con = getCursor()
    con.execute("SELECT signing_key, verify_key FROM profiles WHERE ROWID=?", (profileId,))
    out = con.fetchone() or ()

    return tuple(safe.decrypt(i) for i in out)

def getMessageKeys(safe, profileId):
    """
    Return message encryption private and public keys for a given profile ID

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @return: (private key, public key)
    """
    con = getCursor()
    con.execute("SELECT private_key, public_key FROM profiles WHERE ROWID=?", (profileId,))
    out = con.fetchone() or ()

    return tuple(safe.decrypt(i) for i in out)

def getUidMask(safe, profileId, mask):
    """
    Return original uid associated with given masked id (mask)

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @param mask: masked uid
    @return: original uid
    """
    con = getCursor()
    con.execute("SELECT friend_uid FROM friend_mask WHERE profile_id=? AND friend_mask=?", (profileId, mask))
    out = con.fetchone()

    return safe.decrypt(out[0]) if out is not None else out

def setUidMask(safe, profileId, uid):
    """
    Set new mask value for given user ID

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @param uid: user ID to mask
    @return: localised masked ID for friend
    """
    con = getCursor()

    fmask = str(uuid4())
    con.execute("INSERT INTO friend_mask (profile_id, friend_mask, friend_uid) VALUES (?, ?, ?)",
                [profileId, fmask] + list(encrypt(safe, uid)))

    return fmask

def getMasks(safe, profileId):
    """
    Return all uid->mask values for a given profile

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @return: dictionary of uid->mask
    """
    con = getCursor()
    con.execute("SELECT friend_uid, friend_mask FROM friend_mask WHERE profile_id=?", (profileId,))
    out = con.fetchall()

    return {safe.decrypt(u): m for u, m in out} if out else None

def getFriendAuth(safe, profileId, mask):
    """
    Return profile's mask associated with friend (uid) for authorised server interaction with friend

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @param mask: friend's uid mask
    @return: this profile's mask uid
    """
    con = getCursor()
    con.execute("SELECT auth_token, sent_token FROM friend_auth WHERE profile_id=? AND friend_mask=?", (profileId, mask))
    out = con.fetchone() or ()

    return tuple(safe.decrypt(i) for i in out)

def setFriendAuth(safe, profileId, mask, authToken, sentToken):
    """
    Set profile's authorised mask associated with friend

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @param mask: mask of friend's original UID value (profile specific)
    @param authToken: Authorisation token used for server commands requiring friend authorisation
    @param sentToken: Authorisation token used by friend for server commands regarding us
    """
    con = getCursor()
    con.execute("INSERT INTO friend_auth (profile_id, friend_mask, auth_token, sent_token) VALUES (?, ?, ?, ?)",
                [profileId, mask] + list(encrypt(safe, authToken, sentToken)))

def updateFriendAuth(safe, profileId, mask, authToken=False, sentToken=False):
    """
    Update authorisation tokens in local storage for given friend (mask).

    If authToken or sentToken is False, the parameter set to False will not be updated.
    If authToken or sentToken is None, the parameter set to None will be removed from local storage (set to '').
    If authToken or sentToken is bytes object, the associated fields will be updated with provided bytes object

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @param mask: friend's uid mask
    @param authToken: Authorisation token used for server commands requiring friend authorisation
    @param sentToken: Authorisation token used by friend for server commands regarding us
    """
    con = getCursor()
    if authToken is not False:
        con.execute("UPDATE friend_auth SET auth_token=? WHERE profile_id=? AND friend_mask=?",
                    list(encrypt(safe, authToken)) if authToken is not None else [b''] + [profileId, mask])

    if sentToken is not False:
        con.execute("UPDATE friend_auth SET sent_token=? WHERE profile_id=? AND friend_mask=?",
                    list(encrypt(safe, sentToken)) if sentToken is not None else [b''] + [profileId, mask])

def storeHistory(safe, profileId, mask, message, fromFriend):
    """
    Store messages in database

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @param mask: friend's masked ID
    @param message: message to store
    @param fromFriend: Message was sent by friend (True), instead of being sent by logged in user (False)
    """
    con = getCursor()
    con.execute("INSERT INTO history (profile_id, friend_mask, message, from_friend) VALUES (?, ?, ?, ?)",
                [profileId, mask] + list(encrypt(safe, message, bytes(str(int(fromFriend)), encoding='ascii'))))

def getFriendRequests(safe, profileId, outgoing=True, expire=28):
    """
    Return all current outgoing friend requests

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @param outgoing: True returns all requests we sent out, False returns all requests we've received
    @param expire: number of days friend requests are valid for
    @return: uid -> (message, timestamp, address, row id)
    """
    con = getCursor()
    con.execute("SELECT rowid, uid, message, address, datestamp FROM friend_requests WHERE profile_id=? AND outgoing=?",
                (profileId, outgoing))

    reqs = {}
    delete = []
    now = datetime.utcnow()
    for rowid, uid, msg, addr, timestamp in con.fetchall():
        timestamp = datetime.strptime(safe.decrypt(timestamp).decode(encoding='ascii'),'%Y-%m-%d %H:%M:%S.%f')
        # check for expired friend requests
        check = now - timestamp
        if check.days > expire:
            delete.append(rowid)
        else:
            reqs[safe.decrypt(uid)] = (safe.decrypt(msg), timestamp, safe.decrypt(addr), rowid)

    if delete:
        # delete expired friend requests
        delFriendRequests(delete)

    return reqs

def storeFriendRequest(safe, profileId, uid, message, address, outgoing):
    """
    Store submitted friend request

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @param uid: user ID request was sent to
    @param message: original message sent with request
    @param address: If incoming request, store address information
    @param outgoing: 1 (True) if request sent by us, otherwise 0 (False) if received request
    """
    con = getCursor()
    # timestamp is created on insert
    con.execute("INSERT INTO friend_requests (profile_id, outgoing, uid, address, message, datestamp) VALUES (?, ?, ?, ?, ?, ?)",
                [profileId, outgoing] + list(encrypt(safe, uid, address, message,
                                                     bytes(str(datetime.utcnow()), encoding='ascii'))))

    return con.lastrowid

def delFriendRequests(rowIds, cursor=None):
    """
    Remove request with given row id(s) iterable

    @param rowIds: an iterable of friend request internal row IDs to delete
    @param cursor: database connection cursor object. If None, new cursor will be created.
    """
    if cursor is None:
        cursor = getCursor()

    # be nice and accept singular integers (and even strings)
    try:
        rowIds = (str(int(rowIds)),)
    except TypeError:
        pass

    cursor.execute("DELETE FROM friend_requests WHERE rowid IN (?)", (', '.join(rowIds),))

def getFileRequests(safe, profileId, outgoing, mask=None, expire=7):
    """
    Retrieve all file requests for given profile ID

    @param safe: crypto box
    @param profileId: profile ID of logged in user
    @param outgoing: 1 (True) for file requests sent by logged in user, 0 (False) for received file transfer requests
    @param mask: retrieve file requests to/from this mask. If None, all requests are returned
    @param expire: number of days file transfer requests are valid for
    @return: mask-> checksum-> (filename, size, rowid)
    """
    con = getCursor()
    if mask is None:
        con.execute("SELECT ROWID, friend_mask, filename, checksum, filesize, datestamp FROM file_requests "
                    "WHERE profile_id=? AND outgoing=?", (profileId, outgoing))
    else:
        con.execute("SELECT ROWID, friend_mask, filename, checksum, filesize, datestamp FROM file_requests "
                    "WHERE profile_id=? AND friend_mask=? AND outgoing=?", (profileId, mask, outgoing))

    expire = int(expire)

    delete = []
    now = datetime.utcnow()
    # user file transfer requests, uid -> file req data
    ureqs = defaultdict(dict)
    for rowid, mask, fname, checksum, size, timestamp in con.fetchall():
        timestamp = datetime.strptime(safe.decrypt(timestamp).decode(encoding='ascii'),'%Y-%m-%d %H:%M:%S.%f')
        # check for expired friend requests
        check = now - timestamp
        if check.days > expire:
            delete.append(rowid)
        else:
            ureqs[mask][safe.decrypt(checksum)] = (safe.decrypt(fname), safe.decrypt(size), rowid)

    if delete:
        # delete expired file transfer requests
        delFileRequests(delete)

    # return dict instead of defaultdict
    return {k: v for k, v in ureqs.items()}

def storeFileRequest(safe, profileId, outgoing, mask, request):
    """
    Set file transfer request

    @param safe: crypto box
    @param profileId: logged in profile ID
    @param outgoing: 1 (True) for file requests sent by logged in user, 0 (False) for received file transfer requests
    @param mask: friend mask
    @param request: (filename, size, checksum)
    """
    fname, size, checksum = request

    con = getCursor()
    con.execute("INSERT INTO file_requests (profile_id, outgoing, friend_mask, filename, checksum, filesize, datestamp) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)", [profileId, outgoing, mask] + list(encrypt(safe, fname, checksum, size, bytes(str(datetime.utcnow()), encoding='ascii'))))

    return con.lastrowid


def delFileRequests(rowIds, cursor=None):
    """
    Remove file transfer request with given row id(s) iterable

    @param rowIds: an iterable of file transfer request internal row IDs to delete
    @param cursor: database connection cursor object. If None, new cursor will be created.
    """
    if cursor is None:
        cursor = getCursor()

    # be nice and accept singular integers (and even strings)
    try:
        rowIds = (str(int(rowIds)),)
    except TypeError:
        pass

    cursor.execute("DELETE FROM file_requests WHERE rowid IN (?)", (', '.join(rowIds),))
