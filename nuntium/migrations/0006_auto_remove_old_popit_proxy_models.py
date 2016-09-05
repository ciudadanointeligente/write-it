# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('nuntium', '0005_rename_migrated_fields'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PopitApiInstance',
        ),
        migrations.DeleteModel(
            name='PopitPerson',
        ),
    ]
