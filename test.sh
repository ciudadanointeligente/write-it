#!/bin/bash
set -e
python manage.py test nuntium contactos mailit --failfast
