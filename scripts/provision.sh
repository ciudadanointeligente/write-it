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
sudo DEBIAN_FRONTEND=noninteractive apt-get dist-upgrade -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y git python-dev python-pip libffi-dev libssl-dev rabbitmq-server build-essential

# Instructions from: http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/setup-repositories.html
wget -qO - https://packages.elasticsearch.org/GPG-KEY-elasticsearch | sudo apt-key add -
echo 'deb http://packages.elasticsearch.org/elasticsearch/0.90/debian stable main' | sudo tee /etc/apt/sources.list.d/elasticsearch.list

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y openjdk-6-jre elasticsearch

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

# Set shell login message
echo "-----------------------------------------------
Welcome to the WriteIt vagrant machine

Run the web server with:
  cd /vagrant
  ./manage.py runserver 0.0.0.0:8000

Then visit http://localhost:8000 to use WriteIt
-----------------------------------------------
" | sudo tee /etc/motd.tail > /dev/null
