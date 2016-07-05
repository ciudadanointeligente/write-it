# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('nuntium', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='author_name',
            field=models.CharField(default=b'', max_length=512, blank=True),
            preserve_default=True,
        ),
    ]
