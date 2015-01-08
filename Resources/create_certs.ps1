$env:OPENSSL_CONF='c:\OpenSSL-Win32\bin\openssl.cfg'

$command = 'c:\OpenSSL-Win32\bin\openssl.exe ecparam -genkey -name secp256k1 -out server.key.orig'
iex $command

$command = 'c:\OpenSSL-Win32\bin\openssl.exe req -new -key server.key.orig -out server.csr -subj "/"'
iex "& $command"

$command = 'c:\OpenSSL-Win32\bin\openssl.exe req -x509 -days 365 -key server.key.orig -in server.csr -out server.crt'
iex $command