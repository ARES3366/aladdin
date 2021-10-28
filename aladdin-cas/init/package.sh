#!/bin/sh
pyinstaller start_init_server.py -n aladdin-cas-init -y

# pyinstaller -F  aladdin-cas.spec -y 
# cd dist/aladdin-cas-init

#pip3 freeze > requirements.txt

cd ../
