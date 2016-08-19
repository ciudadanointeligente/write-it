# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('popolo', '0002_update_models_from_upstream'),
        ('instance', '0009_add_related_name_to_popolosource_persons'),
    ]

    operations = [
        migrations.CreateModel(
            name='PopoloPerson',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('popolo.person',),
        ),
        migrations.AlterField(
            model_name='instancemembership',
            name='person',
            field=models.ForeignKey(to='instance.PopoloPerson'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='popolosource',
            name='persons',
            field=models.ManyToManyField(related_name='popolo_sources', to='instance.PopoloPerson'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='writeitinstance',
            name='persons',
            field=models.ManyToManyField(related_name='writeit_instances', through='instance.InstanceMembership', to='instance.PopoloPerson'),
            preserve_default=True,
        ),
    ]
