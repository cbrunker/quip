#
# Utility functions
#
from functools import partial
from uuid import UUID
from hashlib import sha1
from os import path, listdir
from sys import platform
from zipfile import ZipFile
from subprocess import call

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

def checkCerts():
    """
    Checks to see if required TLS certificates exist in Resources directory. Attempts to generate certificates if not found

    @returns: Boolean value based on success
    """
    resDir = path.abspath(path.join(path.dirname(path.abspath(__file__)), path.pardir, 'Resources'))
    command = None

    success = False
    shell = False
    # check to see if required certificates exist
    if not all(True if path.isfile(path.join(resDir, cert)) else False for cert in ('server.crt', 'server.key.orig')):
        ############
        # Check OS
        ############
        if platform in ('linux', 'darwin'):
            # bash script run
            command = 'sh {}'.format(path.join(resDir, 'create_certs_linux.sh'))
            shell = True
        elif platform == 'win32':
            hasOpenSSL = False

            # check for openssl requirement (downloaded during installer run)
            files = sorted((path.isdir(f), f) for f in listdir(resDir) if f.lower().startswith('openssl-'))
            # check for expanded directory and executable
            for isDir, ofile in files:
                if isDir and path.isfile(path.join(resDir, ofile, 'openssl.exe')):
                    hasOpenSSL = True
                    newDir = ofile
                    break

            if not hasOpenSSL and files:
                # sorted filename to list newest version first
                for ofile in sorted(f for isDir, f in files if not isDir and path.splitext(f) == '.zip'):
                    # extract archive
                    with ZipFile(ofile, 'r') as ozip:
                        newDir = path.splitext(ofile)[0]
                        ozip.extractall(path=path.join(resDir, newDir))

                    # verify openssl.exe exists in directory
                    if path.isfile(path.join(newDir, 'openssl.exe')):
                        hasOpenSSL = True
                        break

            if hasOpenSSL:
                # write openssl directory to config file
                with open(path.join(resDir, 'openssl.cfg'), 'w') as config:
                    config.writelines([newDir])

                # windows bat command file
                command = 'cmd /c {}'.format(path.join(resDir, 'create_certs_windows.bat'))

        if command:
            call([command], shell=shell)
            # check command has generated correct files
            if all(True if path.isfile(path.join(resDir, cert)) else False for cert in ('server.crt', 'server.key.orig')):
                success = True
    else:
        success = True

    return success