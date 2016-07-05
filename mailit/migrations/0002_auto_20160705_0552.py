# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nuntium', '0001_initial'),
        ('mailit', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rawincomingemail',
            name='answer',
            field=models.OneToOneField(related_name='raw_email', null=True, to='nuntium.Answer'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rawincomingemail',
            name='writeitinstance',
            field=models.ForeignKey(related_name='raw_emails', to='nuntium.WriteItInstance', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mailittemplate',
            name='writeitinstance',
            field=models.OneToOneField(related_name='mailit_template', to='nuntium.WriteItInstance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bouncedmessagerecord',
            name='outbound_message',
            field=models.OneToOneField(to='nuntium.OutboundMessage'),
            preserve_default=True,
        ),
    ]
