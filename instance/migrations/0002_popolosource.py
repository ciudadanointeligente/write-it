# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('popolo', '0003_auto_20160708_0338'),
        ('instance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PopoloSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(max_length=255)),
                ('persons', models.ManyToManyField(to='popolo.Person')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
