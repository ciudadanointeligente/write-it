#!/bin/bash

# abort on any errors
set -e

# check that we are in the expected directory
cd `dirname $0`/..

source .venv/bin/activate

./manage.py migrate --no-initial-data
