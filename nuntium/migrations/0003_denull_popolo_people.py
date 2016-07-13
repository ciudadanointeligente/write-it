# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('nuntium', '0002_add_parallel_popolo_data'),
        ('instance', '0004_add_django_popolo_people'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='popolo_person',
            field=models.ForeignKey(to='popolo.Person'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='confirmation',
            name='created',
            field=models.DateField(default=datetime.datetime(2016, 7, 13, 11, 56, 16, 829204, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='messagerecord',
            name='datetime',
            field=models.DateField(default=datetime.datetime(2016, 7, 13, 11, 56, 16, 823044, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='nocontactom',
            name='popolo_person',
            field=models.ForeignKey(to='popolo.Person'),
            preserve_default=True,
        ),
    ]
