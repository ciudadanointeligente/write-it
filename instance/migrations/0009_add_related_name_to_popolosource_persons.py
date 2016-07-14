# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0008_remove_writeitinstancepopitinstancerecord_popitapiinstance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='popolosource',
            name='persons',
            field=models.ManyToManyField(related_name='popolo_sources', to='popolo.Person'),
            preserve_default=True,
        ),
    ]
