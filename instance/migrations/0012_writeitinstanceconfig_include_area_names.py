# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0011_update_default_language_choice'),
    ]

    operations = [
        migrations.AddField(
            model_name='writeitinstanceconfig',
            name='include_area_names',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
