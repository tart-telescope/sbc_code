#!/bin/sh
#
# Install the sbc code on a client single board computer
TART=tart@nzdunedin
rsync --recursive --verbose --exclude '*.venv*'  --exclude 'node_modules'  --exclude '*.egg-info' --exclude '*.bak' --exclude '*.pyc' . ${TART}:code/
