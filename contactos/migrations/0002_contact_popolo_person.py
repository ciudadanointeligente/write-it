# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('popolo', '0002_update_models_from_upstream'),
        ('contactos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='popolo_person',
            field=models.ForeignKey(blank=True, to='popolo.Person', null=True),
            preserve_default=True,
        ),
    ]
