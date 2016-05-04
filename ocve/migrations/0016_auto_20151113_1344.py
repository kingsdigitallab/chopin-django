# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocve', '0015_merge_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='annotation',
            name='ocveuser_id',
        ),
        migrations.RemoveField(
            model_name='barcollection',
            name='ocveuser_id',
        ),
    ]
