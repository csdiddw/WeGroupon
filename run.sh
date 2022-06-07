#!/bin/bash

set -euxo pipefail

protoc -I=./proto/ --python_out=./ ./proto/*.proto

if [ $1 == 'gui' ]
then
   ./gui.py $2
else
   ./main.py $2
fi
