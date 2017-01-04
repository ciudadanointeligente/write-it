# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0012_writeitinstanceconfig_include_area_names'),
    ]

    operations = [
        migrations.AlterField(
            model_name='writeitinstancepopitinstancerecord',
            name='updated',
            field=models.DateTimeField(auto_now=True),
            preserve_default=True,
        ),
    ]
