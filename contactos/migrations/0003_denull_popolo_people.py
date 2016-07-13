# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contactos', '0002_contact_popolo_person'),
        ('instance', '0004_add_django_popolo_people'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='popolo_person',
            field=models.ForeignKey(to='popolo.Person'),
            preserve_default=True,
        ),
    ]
