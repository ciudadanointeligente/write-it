#!/bin/bash

# abort on any errors
set -e

# check that we are in the expected directory
cd `dirname $0`/..

# create/update the virtual environment

virtualenv_dir=../virtualenv-writeit
virtualenv_activate="$virtualenv_dir/bin/activate"

if [ ! -f "$virtualenv_activate" ]
then
    # NOTE: some packages are difficult to install if they are not site packages,
    # for example xapian. If using these you might want to add the
    # '--enable-site-packages' argument.
    virtualenv --no-site-packages "$virtualenv_dir"
fi

source "$virtualenv_activate"

# Upgrade pip to a secure version
# curl -L -s https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python
# Revert to the line above once we can get a newer setuptools from Debian, or
# pip ceases to need such a recent one.
curl -L -s https://raw.github.com/mysociety/commonlib/master/bin/get_pip.bash | bash

pip install --requirement requirements.txt
pip install --requirement requirements-mysociety.txt

# make sure that there is no old code (the .py files may have been git deleted)
find . -name '*.pyc' -delete

cp conf/local_settings.py writeit/local_settings.py

# get the database up to speed
./manage.py syncdb --no-initial-data
./manage.py migrate --no-initial-data

./manage.py collectstatic --noinput
