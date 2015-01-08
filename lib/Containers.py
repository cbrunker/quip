#
# Specalised container classes
#
from lib.Database import getMasks, getAddress, getFileRequests, updateAddress
from lib.Exceptions import MissingFriend


class Masks:
    """
    Friend user ID to friend mask mapping
    """
    def __init__(self, safe, profileId, reverse=False):
        """
        Mask container constructor

        @param safe: crypto box
        @param profileId: logged in profile ID
        @param reverse: key and value are swapped, mask becomes the lookup key
        """
        self.safe = safe
        self.profileId = profileId
        # friend uid->mask container
        self.__masks = getMasks(self.safe, self.profileId) or {}

        if reverse:
            self.__masks = {v: k for k, v in self.__masks.items()}

    def __getitem__(self, item):
        """
        @param item: Friend uid (or mask if reversed)
        @return: Friend mask (or uid if reversed)
        """
        try:
            value = self.__masks[item]
        except KeyError:
            self.__masks = getMasks(self.safe, self.profileId)
            value = self.__masks.get(item, None)
            if value is None:
                raise MissingFriend("Friend does not exist locally: {}".format(item))
        
        return value


class Friends:
    """
    Friend container to provide IP and Port information
    """
    def __init__(self, safe, profileId):
        """
        Friend container constructor

        @param safe: crypto box
        @param profileId: logged in profile ID
        """
        self.safe = safe
        self.profileId = profileId
        self.__friends = {}
        # friend uid->mask container
        self.__masks = Masks(safe, profileId)

    def __getitem__(self, uid):
        """
        @param uid: Friend user id
        @return: last known (ip, port)
        """
        try:
            addr = self.__friends[uid]
        except KeyError:
            addr = tuple(getAddress(self.safe, self.profileId, self.__masks[uid]).decode('ascii').split(':'))
            self.__friends[uid] = addr

        return addr

    def __setitem__(self, uid, address):
        """
        Used when address of a friend requires updating

        @param uid: Friend user uid
        @param address: 'ip:port' address information for user
        """
        # raise KeyError exception if uid does not exist
        if address != self.__friends[uid]:
            updateAddress(self.safe, self.profileId, self.__masks[uid], address)
            self.__friends[uid] = address

    def __iter__(self):
        for k, v in self.__friends.items():
            yield k, v

    def items(self):
        return self.__friends.items()

class FileRequests:
    """
    File requests container
    """
    def __init__(self, safe, profileId, outgoing=False):
        """
        File requests contructor

        @param safe: crypto box
        @param profileId: logged in profile ID
        @param outgoing: True to contain requests this user sent, False to contain received file transfer requests
        """
        self.safe = safe
        self.profileId = profileId
        self.outgoing = outgoing
        self.__requests = getFileRequests(safe, profileId, outgoing)

    def __getitem__(self, uid):
        """
        @param uid: Friend user id
        @return: friend's file sending requests
        """
        try:
            requests = self.__requests[uid]
        except KeyError:
            # reload in case of new request
            self.reload()
            # throw KeyError if request not found
            requests = self.__requests[uid]

        return requests

    def __len__(self):
        """
        Return number of loaded requests.
        @return: integer
        """
        return len(self.__requests.values())

    def __iter__(self):
        for k, v in self.__requests.items():
            yield k, v

    def keys(self):
        return self.__requests.keys()

    def items(self):
        return self.__requests.items()

    def reload(self):
        self.__requests = getFileRequests(self.safe, self.profileId, self.outgoing)