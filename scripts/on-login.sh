#!/bin/sh

# Run by ~/.profile when users log into the Vagrant VM

printf '\n\033[1;32m'
echo 'Welcome to the WriteIt vagrant machine'
echo 'Run the web server with:'
echo '  cd /vagrant'
echo '  ./manage.py runserver 0.0.0.0:8000'
echo 'Then visit http://localhost:8000 to use WriteIt'
printf '\033[0m\n'
