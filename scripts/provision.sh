#!/bin/sh

# Stop script execution as soon as there are any errors
set -e

pwd
now=$(date +"%T")
echo "$now Running provision.sh"

# Use the en_GB.utf8 locale
sudo update-locale LANG=en_GB.utf8

# Install the packages we need
sudo apt-get update
sudo apt-get install -y git python-dev python-pip libffi-dev libssl-dev

# :TODO: Set up a virtualenv, to protect us
# from system python packages

# Install the python requirements
# We specify a long timeout and use-mirrors to avoid
# errors like "SSLError: The read operation timed out"
cd /vagrant
sudo pip install --timeout=120 --use-mirrors -r requirements.txt

# Set up the Django database
./manage.py syncdb --noinput
./manage.py migrate

# Set on-login.sh to be run when the user logs in
echo '' >> ~/.profile
echo '/vagrant/scripts/on-login.sh' >> ~/.profile

echo
echo '** Your Vagrant box is ready to use! \o/ **'
echo 'Log in (with vagrant ssh) and follow the instructions.'
