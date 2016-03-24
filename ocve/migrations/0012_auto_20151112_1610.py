# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocve', '0011_auto_20151112_1608'),
    ]

    operations = [
        migrations.RenameField(
            model_name='annotation',
            old_name='user',
            new_name='user_id',
        ),
    ]
