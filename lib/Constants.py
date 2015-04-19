#
# Constants used throughout the library
#

######################
# P2P Server Commands
######################
REQ_FRIEND = 12012201
REQ_FILE = 99119840
RECV_FILE = 99119841
RECV_MSG = 78986713
RECV_AVATAR = 57383752
INVITE_CHAT = 86878161

#########################
# Quip Server Commands
#########################
LOGIN_NEW = 60610262
LOGIN_DEL = 98198192

LOGIN = 81721222
LOGOUT = 99570102

STATUS_SET = 56191324

MESSAGES_GET = 70771918
MESSAGE_STORE = 47422111

FRIENDLIST_GET = 10181108

FRIEND_REQUEST = 88067180
FRIEND_REQUEST_DEL = 56671276
FRIEND_REQUESTS_GET = 79944333

PROFILE_GET = 19192491
PROFILE_SET = 74310221
PROFILE_SEARCH = 97929722

AUTH_TOKEN_GET = 88781870
AUTH_TOKEN_SET = 47422013
AUTH_TOKEN_DEL = 56671031

RECOVERY_EMAIL = 65663422
RECOVERY_CODE = 65663424

DETAILS_GET = 17549000

INVITES_GET = 35433331
INVITES_CLEAR = 35433332
INVITES_GENERATE = 47422112

#########
# Limits
#########
# command length for received commands
COMMAND_LENGTH = 8
# friend request maximum message length
FRIEND_REQUEST_LEN = 110
# Max char limit for profile storage
LIMIT_PROFILE_VALUES = {'first': 16, 'last': 32, 'alias': 16, 'comment': 128, 'country': 64, 'state': 64, 'city': 64,
                        'email': 255}
# avatar size limit in bytes
LIMIT_AVATAR_SIZE = 131072
# age of message being received in seconds
LIMIT_MESSAGE_TIME = 600

#################################
# Pre-defined byte return values
#################################
BTRUE = b'1'
BFALSE = b'0'
INVALID_COMMAND = b'10000001'
INVALID_DATA = b'10000002'
NONEXISTANT = b'10000003'
MODIFIED_FILE = b'10000004'
TIMEOUT = b'20000001'

FAILURE_COMMANDS = {INVALID_COMMAND, INVALID_DATA, TIMEOUT}

################
# User Statuses
################
STATUS_ONLINE = 7071170
STATUS_OFFLINE = 5656232
STATUS_AWAY = 8909812
STATUS_INVISIBLE = 3201208
STATUS_BUSY = 1248121
STATUSES_BASIC = {STATUS_ONLINE: 'online',
                  STATUS_OFFLINE: 'offline',
                  STATUS_AWAY: 'away',
                  STATUS_BUSY: 'busy',
                  STATUS_INVISIBLE: 'invisible'}

#################
# Misc Constants
#################
# profile data tokens
PROFILE_ENTRY_SEPARATOR = '\u0091'
PROFILE_VALUE_SEPARATOR = '\u0092'
# Profile fields
PROFILE_FIELDS = frozenset(LIMIT_PROFILE_VALUES)
# newline character as bytes
WRITE_END = b'\n'
# Server client connection timelimit
TCP_TIMEOUT = 10


################
# Quip Server
################
SERVER = 'quip.im'
#SERVER_IPv4 = '106.186.28.218'
SERVER_IPv4 = '127.0.0.1'
SERVER_PORT = 8822

########
# URLs
########
URL_PATRONAGE = 'https://www.quip.im/patron'
