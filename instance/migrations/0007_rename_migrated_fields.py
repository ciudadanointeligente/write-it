# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0006_remove_old_fields'),
    ]

    operations = [
        migrations.RenameField(
            model_name='writeitinstance',
            old_name='popolo_persons',
            new_name='persons',
        ),
    ]
