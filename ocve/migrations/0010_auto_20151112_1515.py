# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocve', '0009_delete_treetype'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uncertain',
            name='pageimage',
        ),
        migrations.RemoveField(
            model_name='uncertain',
            name='source',
        ),
        migrations.DeleteModel(
            name='Uncertain',
        ),
    ]
