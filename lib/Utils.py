#
# Utility functions
#
from functools import partial
from uuid import UUID
from hashlib import sha1

import nacl.utils
import nacl.secret

def isValidUUID(uid):
    """
    Validate UUID

    @param uid: UUID value to be verfied, can be bytes or str
    @return: True if UUID valid, else False
    """
    try:
        # attempt convertion from bytes to str
        uid = uid.decode('ascii')
    except AttributeError:
        # is already bytes object
        pass
    except UnicodeDecodeError:
        # uid contains non-ascii characters, invalid UUID
        return False

    try:
        out = UUID(uid, version=4)
    except ValueError:
        return False

    # check converted value from UUID equals original value. UUID class is not strict on input
    return str(out) == uid

def encrypt(safe, *args):
    """
    Encrypt all provided data

    @param safe: encryption class
    @param args: data to be encrypted
    @return: encryption output iterable
    """
    return (safe.encrypt(a, nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)) for a in args)

def sha1sum(filePath, blocksize=1024):
    """
    Calculate SHA1 hash of file

    @param filePath: Path to hashable file
    @param blocksize: Amount of bytes to read into memory before hashing
    @return: SHA1 hash value (bytes)
    """
    with open(filePath, mode='rb') as f:
        out = sha1()
        for buf in iter(partial(f.read, blocksize), b''):
            out.update(buf)

    return bytes(out.hexdigest(), encoding='ascii')
