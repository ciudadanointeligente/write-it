# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contactos', '0001_initial'),
        ('nuntium', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='writeitinstance',
            field=models.ForeignKey(related_name='contacts', to='nuntium.WriteItInstance', null=True),
            preserve_default=True,
        ),
    ]
