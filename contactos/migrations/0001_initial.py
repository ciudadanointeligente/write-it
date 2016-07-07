# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('popit', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('instance', '0001_initial'),
     ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=512)),
                ('is_bounced', models.BooleanField(default=False)),
                ('popit_identifier', models.CharField(max_length=512, null=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('label_name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='contact',
            name='contact_type',
            field=models.ForeignKey(to='contactos.ContactType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contact',
            name='owner',
            field=models.ForeignKey(related_name='contacts', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contact',
            name='person',
            field=models.ForeignKey(to='popit.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contact',
            name='writeitinstance',
            field=models.ForeignKey(related_name='contacts', to='instance.WriteItInstance', null=True),
            preserve_default=True,
        ),
    ]
