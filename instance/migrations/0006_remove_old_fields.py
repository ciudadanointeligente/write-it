# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0005_denull_popolo_source'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='membership',
            name='person',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='writeitinstance',
        ),
        migrations.RemoveField(
            model_name='writeitinstance',
            name='persons',
        ),
        migrations.DeleteModel(
            name='Membership',
        ),
    ]
