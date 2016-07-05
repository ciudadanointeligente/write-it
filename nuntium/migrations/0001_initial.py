# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
import datetime
from django.utils.timezone import utc
from django.conf import settings
import annoying.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contactos', '0001_initial'),
        ('popit', '__first__'),
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
                ('created', models.DateField(default=datetime.datetime(2016, 7, 5, 10, 52, 14, 551097, tzinfo=utc))),
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
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('person', models.ForeignKey(to='popit.Person')),
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
                ('datetime', models.DateField(default=datetime.datetime(2016, 7, 5, 10, 52, 14, 538844, tzinfo=utc))),
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
        migrations.CreateModel(
            name='WriteItInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=512, blank=True)),
                ('slug', autoslug.fields.AutoSlugField(populate_from=b'name', unique=True, editable=False)),
                ('owner', models.ForeignKey(related_name='writeitinstances', to=settings.AUTH_USER_MODEL)),
                ('persons', models.ManyToManyField(related_name='writeit_instances', through='nuntium.Membership', to='popit.Person')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WriteItInstanceConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('testing_mode', models.BooleanField(default=True)),
                ('moderation_needed_in_all_messages', models.BooleanField(default=False, help_text='Every message is going to         have a moderation mail')),
                ('allow_messages_using_form', models.BooleanField(default=True, help_text='Allow the creation of new messages         using the web')),
                ('rate_limiter', models.IntegerField(default=0)),
                ('notify_owner_when_new_answer', models.BooleanField(default=False, help_text='The owner of this instance         should be notified         when a new answer comes in')),
                ('autoconfirm_api_messages', models.BooleanField(default=True, help_text='Messages pushed to the api should             be confirmed automatically')),
                ('custom_from_domain', models.CharField(max_length=512, null=True, blank=True)),
                ('email_host', models.CharField(max_length=512, null=True, blank=True)),
                ('email_host_password', models.CharField(max_length=512, null=True, blank=True)),
                ('email_host_user', models.CharField(max_length=512, null=True, blank=True)),
                ('email_port', models.IntegerField(null=True, blank=True)),
                ('email_use_tls', models.NullBooleanField()),
                ('email_use_ssl', models.NullBooleanField()),
                ('can_create_answer', models.BooleanField(default=False, help_text=b'Can create an answer using the WebUI')),
                ('maximum_recipients', models.PositiveIntegerField(default=5)),
                ('default_language', models.CharField(max_length=10, choices=[(b'ar', b'Arabic'), (b'cs', b'Czech'), (b'en', b'English'), (b'es', b'Spanish'), (b'fr', b'French'), (b'hu', b'Hungarian')])),
                ('writeitinstance', annoying.fields.AutoOneToOneField(related_name='config', to='nuntium.WriteItInstance')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WriteitInstancePopitInstanceRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('periodicity', models.CharField(default=b'1W', max_length=b'2', choices=[(b'--', b'Never'), (b'2D', b'Twice every Day'), (b'1D', b'Daily'), (b'1W', b'Weekly')])),
                ('status', models.CharField(default=b'nothing', max_length=b'20', choices=[(b'nothing', 'Not doing anything now'), (b'error', 'Error'), (b'success', 'Success'), (b'waiting', 'Waiting'), (b'inprogress', 'In Progress')])),
                ('status_explanation', models.TextField(default=b'')),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('popitapiinstance', models.ForeignKey(to='popit.ApiInstance')),
                ('writeitinstance', models.ForeignKey(to='nuntium.WriteItInstance')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ratelimiter',
            name='writeitinstance',
            field=models.ForeignKey(to='nuntium.WriteItInstance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='newanswernotificationtemplate',
            name='writeitinstance',
            field=models.OneToOneField(related_name='new_answer_notification_template', to='nuntium.WriteItInstance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='message',
            name='writeitinstance',
            field=models.ForeignKey(to='nuntium.WriteItInstance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='membership',
            name='writeitinstance',
            field=models.ForeignKey(to='nuntium.WriteItInstance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='confirmationtemplate',
            name='writeitinstance',
            field=models.OneToOneField(to='nuntium.WriteItInstance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='confirmation',
            name='message',
            field=models.OneToOneField(to='nuntium.Message'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='answerwebhook',
            name='writeitinstance',
            field=models.ForeignKey(related_name='answer_webhooks', to='nuntium.WriteItInstance'),
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
