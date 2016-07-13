# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0004_add_django_popolo_people'),
    ]

    operations = [
        migrations.AlterField(
            model_name='writeitinstancepopitinstancerecord',
            name='popolo_source',
            field=models.ForeignKey(to='instance.PopoloSource'),
            preserve_default=True,
        ),
    ]
