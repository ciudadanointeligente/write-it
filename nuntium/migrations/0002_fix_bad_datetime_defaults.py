# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('nuntium', '0002_author_name_allow_blank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmation',
            name='created',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='messagerecord',
            name='datetime',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=True,
        ),
    ]
