# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('nuntium', '0004_remove_old_fields'),
    ]

    operations = [
        migrations.RenameField(
            model_name='answer',
            old_name='popolo_person',
            new_name='person',
        ),
        migrations.RenameField(
            model_name='nocontactom',
            old_name='popolo_person',
            new_name='person',
        ),
    ]
