# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0003_add_name_and_email_match_config_option'),
    ]

    operations = [
        migrations.AddField(
            model_name='writeitinstanceconfig',
            name='real_name_for_site_emails',
            field=models.TextField(default=b'', help_text='The name that should appear in the From: line of emails sent from this site', blank=True),
            preserve_default=True,
        ),
    ]
