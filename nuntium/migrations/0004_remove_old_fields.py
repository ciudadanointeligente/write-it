# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nuntium', '0003_denull_popolo_people'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answer',
            name='person',
        ),
        migrations.RemoveField(
            model_name='nocontactom',
            name='person',
        ),
    ]
