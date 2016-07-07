# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0001_initial'),
        ('popit', '__first__'),
        ('contactos', '0001_initial'),
        ('sites', '0001_initial'),
        ('djangoplugins', '__first__'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('content_html', models.TextField()),
                ('created', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AnswerAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.FileField(upload_to=b'attachments/%Y/%m/%d')),
                ('name', models.CharField(default=b'', max_length=512)),
                ('answer', models.ForeignKey(related_name='attachments', to='nuntium.Answer')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AnswerWebHook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(max_length=255)),
                ('writeitinstance', models.ForeignKey(related_name='answer_webhooks', to='instance.WriteItInstance')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Confirmation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=64)),
                ('created', models.DateField(default=datetime.datetime(2016, 7, 6, 11, 35, 48, 122076, tzinfo=utc))),
                ('confirmated_at', models.DateField(default=None, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConfirmationTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_html', models.TextField(help_text='You can use {author_name}, {site_name}, {subject}, {content}, {recipients}, {confirmation_url}, and {message_url}', blank=True)),
                ('content_text', models.TextField(help_text='You can use {author_name}, {site_name}, {subject}, {content}, {recipients}, {confirmation_url}, and {message_url}', blank=True)),
                ('subject', models.CharField(help_text='You can use {author_name}, {site_name}, {subject}, {content}, {recipients}, {confirmation_url}, and {message_url}', max_length=512, blank=True)),
                ('writeitinstance', models.OneToOneField(to='instance.WriteItInstance')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author_name', models.CharField(max_length=512)),
                ('author_email', models.EmailField(max_length=75)),
                ('subject', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('confirmated', models.BooleanField(default=False)),
                ('slug', models.SlugField(unique=True, max_length=255)),
                ('public', models.BooleanField(default=True)),
                ('moderated', models.NullBooleanField()),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('writeitinstance', models.ForeignKey(to='instance.WriteItInstance')),
            ],
            options={
                'ordering': ['-created'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=255)),
                ('datetime', models.DateField(default=datetime.datetime(2016, 7, 6, 11, 35, 48, 116612, tzinfo=utc))),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Moderation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=256)),
                ('message', models.OneToOneField(related_name='moderation', to='nuntium.Message')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NewAnswerNotificationTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('template_html', models.TextField(help_text='You can use {author_name}, {person}, {subject}, {content}, {message_url}, and {site_name}', blank=True)),
                ('template_text', models.TextField(help_text='You can use {author_name}, {person}, {subject}, {content}, {message_url}, and {site_name}', blank=True)),
                ('subject_template', models.CharField(help_text='You can use {author_name}, {person}, {subject}, {content}, {message_url}, and {site_name}', max_length=255, blank=True)),
                ('writeitinstance', models.OneToOneField(related_name='new_answer_notification_template', to='instance.WriteItInstance')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NoContactOM',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'new', max_length=b'10', choices=[(b'new', 'Newly created'), (b'ready', 'Ready to send'), (b'sent', 'Sent'), (b'error', 'Error sending it'), (b'needmodera', 'Needs moderation')])),
                ('message', models.ForeignKey(to='nuntium.Message')),
                ('person', models.ForeignKey(to='popit.Person')),
                ('site', models.ForeignKey(to='sites.Site')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OutboundMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'new', max_length=b'10', choices=[(b'new', 'Newly created'), (b'ready', 'Ready to send'), (b'sent', 'Sent'), (b'error', 'Error sending it'), (b'needmodera', 'Needs moderation')])),
                ('contact', models.ForeignKey(to='contactos.Contact')),
                ('message', models.ForeignKey(to='nuntium.Message')),
                ('site', models.ForeignKey(to='sites.Site')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OutboundMessageIdentifier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=255)),
                ('outbound_message', models.OneToOneField(to='nuntium.OutboundMessage')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OutboundMessagePluginRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sent', models.BooleanField(default=False)),
                ('number_of_attempts', models.PositiveIntegerField(default=0)),
                ('try_again', models.BooleanField(default=True)),
                ('outbound_message', models.ForeignKey(to='nuntium.OutboundMessage')),
                ('plugin', models.ForeignKey(to='djangoplugins.Plugin')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RateLimiter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75)),
                ('day', models.DateField()),
                ('count', models.PositiveIntegerField(default=1)),
                ('writeitinstance', models.ForeignKey(to='instance.WriteItInstance')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75)),
                ('message', models.ForeignKey(related_name='subscribers', to='nuntium.Message')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='confirmation',
            name='message',
            field=models.OneToOneField(to='nuntium.Message'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='answer',
            name='message',
            field=models.ForeignKey(related_name='answers', to='nuntium.Message'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='answer',
            name='person',
            field=models.ForeignKey(to='popit.Person'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='NeedingModerationMessage',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('nuntium.message',),
        ),
        migrations.CreateModel(
            name='PopitApiInstance',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('popit.apiinstance',),
        ),
        migrations.CreateModel(
            name='PopitPerson',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('popit.person',),
        ),
    ]
