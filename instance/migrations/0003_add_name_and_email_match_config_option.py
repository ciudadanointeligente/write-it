# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0002_writeitinstanceconfig_allow_anonymous_messages'),
    ]

    operations = [
        migrations.AddField(
            model_name='writeitinstanceconfig',
            name='email_and_name_must_match',
            field=models.BooleanField(default=False, help_text='When showing other messages by the same author, the public name must match as well as the hidden email'),
            preserve_default=True,
        ),
    ]
