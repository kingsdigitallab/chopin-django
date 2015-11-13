# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ocve', '0012_auto_20151112_1610'),
    ]

    operations = [
        migrations.RenameField(
            model_name='annotation',
            old_name='user_id',
            new_name='ocveuser_id',
        ),
        migrations.AddField(
            model_name='annotation',
            name='user',
            field=models.ForeignKey(default=11, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
