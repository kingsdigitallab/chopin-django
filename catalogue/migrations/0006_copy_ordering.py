# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0005_auto_20150526_1529'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='copy',
            options={'ordering': ['-created'], 'verbose_name_plural': 'Copies'},
        ),
    ]
