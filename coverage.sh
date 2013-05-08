#!/bin/bash
set -e
coverage run --source=nuntium,contactos,mailit manage.py test nuntium contactos mailit
coverage report -m
