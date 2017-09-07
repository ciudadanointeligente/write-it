# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nuntium', '0003_add_parallel_popolo_data'),
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
            model_name='nocontactom',
            name='popolo_person',
            field=models.ForeignKey(to='popolo.Person'),
            preserve_default=True,
        ),
    ]
