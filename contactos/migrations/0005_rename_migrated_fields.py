# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contactos', '0004_remove_contact_person'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contact',
            old_name='popolo_person',
            new_name='person',
        ),
    ]
