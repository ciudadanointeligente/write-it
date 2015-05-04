#!/bin/bash
set -e
source /home/writeit/.virtualenvs/writeit/bin/activate
cd /home/writeit/write-it/
python manage.py handleemail
