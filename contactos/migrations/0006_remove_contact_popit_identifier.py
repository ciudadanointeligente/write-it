# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contactos', '0005_rename_migrated_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contact',
            name='popit_identifier',
        ),
    ]
