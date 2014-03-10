#!/usr/bin/env python
from django.core.management import call_command
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "writeit.settings")
call_command('test','nuntium', 'contactos', 'mailit', verbosity=2)

