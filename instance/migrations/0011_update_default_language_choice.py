# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0010_add_popoloperson_proxy_and_change_related'),
    ]

    operations = [
        migrations.AlterField(
            model_name='writeitinstanceconfig',
            name='default_language',
            field=models.CharField(max_length=10, choices=[(b'ar', b'Arabic'), (b'cs', b'Czech'), (b'en', b'English'), (b'es', b'Spanish'), (b'fa', b'Persian'), (b'fr', b'French'), (b'hu', b'Hungarian')]),
            preserve_default=True,
        ),
    ]
