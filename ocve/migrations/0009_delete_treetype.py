# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocve', '0008_auto_20150617_1039'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TreeType',
        ),
    ]
