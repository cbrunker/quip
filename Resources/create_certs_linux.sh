#!/bin/sh
#
# OSX / Linux / BSD certificate generation
#
# Certificates will be created in the current directory.
#

openssl ecparam -genkey -name secp256k1 -out server.key.orig
openssl req -new -key server.key.orig -out server.csr -subj "/"
openssl req -x509 -days 365 -key server.key.orig -in server.csr -out server.crt

# if run outside of resources directory, check for resources directory and move certificates as required
resources="Resources/"
if [ -d "$resources" ]; then
    mv server.key.orig ${resources}
    mv server.csr ${resources}
    mv server.crt ${resources}
fi
