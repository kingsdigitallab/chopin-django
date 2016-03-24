# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocve', '0016_auto_20151113_1344'),
    ]

    operations = [
        migrations.DeleteModel(
            name='OCVEUser',
        ),
    ]
