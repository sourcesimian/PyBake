#!/bin/bash

export PIP_DOWNLOAD_CACHE=./.cache
mkdir -p $PIP_DOWNLOAD_CACHE

declare -f deactivate >/dev/null && deactivate
rm -rf ./virtualenv

python3 -m venv virtualenv
. ./virtualenv/bin/activate

if [ ! -e "$PIP_DOWNLOAD_CACHE/get-pip.py" ]; then
    curl -o "$PIP_DOWNLOAD_CACHE/get-pip.py" https://bootstrap.pypa.io/get-pip.py
fi
cat "$PIP_DOWNLOAD_CACHE/get-pip.py" | python

pip install pytest flake8

python ./setup.py develop
