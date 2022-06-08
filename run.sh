#!/bin/bash

set -euxo pipefail

protoc -I=./proto/ --python_out=./ ./proto/*.proto

if [ $# -ne 1 ] && [ $# -ne 2 ]
then
   echo "USAGE: ./run.sh gui(cli) appID(optional)"
   exit 1;
fi

if [ $1 == 'gui' ]
then
      if [ $# == 2 ]
      then
         ./gui.py $2
      else
         ./gui.py
      fi
elif [ $1 == 'cli' ]
then
      if [ $# == 2 ]
      then
         ./main.py $2
      else
         ./main.py
      fi
fi