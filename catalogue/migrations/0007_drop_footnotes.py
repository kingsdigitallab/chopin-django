# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0006_copy_ordering'),
    ]

    operations = [
    ]

    migrations.RunSQL(
        ("ALTER TABLE catalogue_richtextpage drop column if EXISTS footnotes;"),
    )
