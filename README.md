Quip - Secure Instant Messaging
===============================

[Quip](http://quip.com) is a peer to peer instant messaging platform built around security and encryption. The available 
Quip client has been developed to provide a clean and easy to use interface while all the security and privacy business 
happens in the background.


Open Source
-----------

The Quip client is completely open source, allowing transparency, review and feedback on the source code. The aim is to 
ensure a secure messaging platform with no hidden or closed code. See the [LICENSE](https://github.com/quip/LICENSE`) 
file for further licensing information.

Peer to Peer
------------

The Quip Client connects directly to contacts, all message communication is directly transfered to the intended contact 
in an encrypted data stream.

Encryption
----------

Quip utilises multiple encryption types, all utilised encryption types are regarded as secure and safe forms of encryption.

* Storage: Salsa20 with Poly1305 MAC
* Identification:
  * Public Keys: Ed25519 
  * Signatures: Curve25519
* Offline Message Storage: Curve25519
* Message Communication: TLSv1.2 with secp256k1
* Server Communication: TLSv1.2 with secp256k1

Privacy
-------

The Quip client stores all information in an encrypted state on a per profile level, data transmitted to the server is 
done via an encrypted data stream and any private information is encrypted by the Quip client before being temporarily 
stored on the server (i.e. offline message storage).