# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0007_rename_migrated_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='writeitinstancepopitinstancerecord',
            name='popitapiinstance',
        ),
    ]
