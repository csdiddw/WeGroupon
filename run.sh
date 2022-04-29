#!/bin/bash

set -euxo pipefail

protoc -I=./proto/ --python_out=./ ./proto/*.proto

./main.py