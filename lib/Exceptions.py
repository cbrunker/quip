#
# Exceptions module
#

# Raised when attempting authenticated Quip Server commands without first logging in
class NotLoggedIn(Exception): pass

# Raised when unable to log in (e.g. invalid login details)
class LoginFailure(Exception): pass

# Raised when IP address information can not be found locally for friend/user
class MissingFriendAddress(Exception): pass

# Raised when unable to successfully connect to destination
class ConnectionFailure(Exception): pass

# Raised when referencing a friend which does not exist
class MissingFriend(Exception): pass

# Raised when authorisation token provided by friend is no longer valid
class Unauthorised(Exception): pass

# Raised when computed file hash does not equal stored hash for file
class FileCorruption(Exception): pass

# Raised when sending data failed
class SendFailure(Exception): pass

# Raised when friendship handshake does not complete successfully, may also be raised due to other friendship failures
class FriendshipFailure(Exception): pass

# Raised when data parsed to client functions (for server interaction) does not pass validation
class InvalidClientData(Exception): pass
