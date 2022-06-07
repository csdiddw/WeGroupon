#!/bin/bash

set -euxo pipefail

protoc -I=./proto/ --python_out=./ ./proto/*.proto

# if the first arg is gui
echo $1
if [ $1 == 'gui' ]
then
   ./gui.py
else
   ./main.py
fi
