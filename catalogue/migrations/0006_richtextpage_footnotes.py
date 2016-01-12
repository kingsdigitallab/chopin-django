# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0005_auto_20150526_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='richtextpage',
            name='footnotes',
            field=wagtail.wagtailcore.fields.RichTextField(default=' '),
            preserve_default=False,
        ),
    ]
