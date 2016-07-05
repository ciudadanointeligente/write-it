# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nuntium', '0001_initial'),
        ('instance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BouncedMessageRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bounce_text', models.TextField()),
                ('date', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MailItTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject_template', models.CharField(default=b'{subject}', help_text='You can use {subject}, {content}, {person}, {author}, {site_url}, {site_name}, and {owner_email}', max_length=255)),
                ('content_template', models.TextField(help_text='You can use {subject}, {content}, {person}, {author}, {site_url}, {site_name}, and {owner_email}', blank=True)),
                ('content_html_template', models.TextField(help_text='You can use {subject}, {content}, {person}, {author}, {site_url}, {site_name}, and {owner_email}', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RawIncomingEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('problem', models.BooleanField(default=False)),
                ('message_id', models.CharField(default=b'', max_length=2048)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='rawincomingemail',
            name='answer',
            field=models.OneToOneField(related_name='raw_email', null=True, to='nuntium.Answer'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rawincomingemail',
            name='writeitinstance',
            field=models.ForeignKey(related_name='raw_emails', to='instance.WriteItInstance', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mailittemplate',
            name='writeitinstance',
            field=models.OneToOneField(related_name='mailit_template', to='instance.WriteItInstance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bouncedmessagerecord',
            name='outbound_message',
            field=models.OneToOneField(to='nuntium.OutboundMessage'),
            preserve_default=True,
        ),
    ]
