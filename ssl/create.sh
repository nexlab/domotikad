#!/bin/bash
openssl genrsa -out privkey.key 2048
openssl req -new -x509 -key privkey.key -out cacert.crt -days 3650
