-- profiles table to store localised and remote account information
CREATE TABLE profiles(
  uid         BLOB,
  auth        BLOB,
  signing_key BLOB,
  verify_key  BLOB,
  private_key BLOB,
  public_key  BLOB,
  avatar      BLOB,
  buffer      BLOB,
  alias       TEXT
);

-- store masked user id information in clear text while encrypting real user id
CREATE TABLE friend_mask(
  profile_id  INTEGER,
  friend_mask TEXT,
  friend_uid  BLOB
);

-- friend verification and decryption keys and localised friend data
CREATE TABLE friends(
  profile_id  INTEGER,
  friend_mask TEXT,
  alias       BLOB,
  avatar      BLOB,
  checksum    BLOB,
  verify_key  BLOB,
  public_key  BLOB,
  
  FOREIGN KEY(friend_mask) REFERENCES friend_mask(friend_mask)
);

-- server authorisation tokens for each friend
CREATE TABLE friend_auth(
  profile_id  INTEGER,
  friend_mask TEXT,
  auth_token  BLOB,
  sent_token  BLOB,
  
  FOREIGN KEY(friend_mask) REFERENCES friend_mask(friend_mask)
);

-- last known address for given friend
CREATE TABLE address(
  profile_id  INTEGER,
  friend_mask TEXT,
  address     BLOB,
  
  FOREIGN KEY(friend_mask) REFERENCES friend_mask(friend_mask)
);

-- stored conversation history
CREATE TABLE history(
  profile_id  INTEGER,
  friend_mask TEXT,
  message     BLOB,
  from_friend BLOB,
  
  FOREIGN KEY(friend_mask) REFERENCES friend_mask(friend_mask)
);

-- current pending friend requests
CREATE TABLE friend_requests(
  profile_id  INTEGER,
  outgoing    INTEGER,
  uid         BLOB,
  address     BLOB,
  message     BLOB,
  datestamp   BLOB
);

-- current pending file transfer requests
CREATE TABLE file_requests(
  profile_id  INTEGER,
  friend_mask INTEGER,
  outgoing    INTEGER,
  filename    BLOB,
  checksum    BLOB,
  filesize    BLOB,
  datestamp   BLOB,

  FOREIGN KEY(friend_mask) REFERENCES friend_mask(friend_mask)
);