# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
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
    ]
