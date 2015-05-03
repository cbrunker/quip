@ECHO OFF

set /p executableLocation=<openssl.cfg

"%executableLocation%\openssl.exe" ecparam -genkey -name secp256k1 -out server.key.orig

"%executableLocation%\openssl.exe" req -new -key server.key.orig -out server.csr -subj "/"

"%executableLocation%\openssl.exe" req -x509 -days 365 -key server.key.orig -in server.csr -out server.crt
