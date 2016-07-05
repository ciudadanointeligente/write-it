# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='writeitinstanceconfig',
            name='allow_anonymous_messages',
            field=models.BooleanField(default=False, help_text='Messages can have empty Author             names'),
            preserve_default=True,
        ),
    ]
