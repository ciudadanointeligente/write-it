# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('popolo', '0002_update_models_from_upstream'),
        ('nuntium', '0002_fix_bad_datetime_defaults'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='popolo_person',
            field=models.ForeignKey(blank=True, to='popolo.Person', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nocontactom',
            name='popolo_person',
            field=models.ForeignKey(blank=True, to='popolo.Person', null=True),
            preserve_default=True,
        ),
    ]
