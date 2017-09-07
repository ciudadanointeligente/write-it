# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('nuntium', '0006_auto_remove_old_popit_proxy_models'),
        ('instance', '0010_add_popoloperson_proxy_and_change_related'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='person',
            field=models.ForeignKey(to='instance.PopoloPerson'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='nocontactom',
            name='person',
            field=models.ForeignKey(to='instance.PopoloPerson'),
            preserve_default=True,
        ),
    ]
