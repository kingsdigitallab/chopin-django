# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocve', '0010_auto_20151112_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='user',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='barcollection',
            name='user_id',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
    ]
