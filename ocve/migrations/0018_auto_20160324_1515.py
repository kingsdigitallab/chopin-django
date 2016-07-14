# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    def set_live(apps, schema_editor):
        Source = apps.get_model('ocve', 'Source')
        for s in Source.objects.all():
            if s.ocve == True or s.cfeo == True:
                s.live=True
                s.save()

    def reset_live(apps, schema_editor):
        Source = apps.get_model('ocve', 'Source')
        for s in Source.objects.all():
                s.live=False
                s.save()

    dependencies = [
        ('ocve', '0017_delete_ocveuser'),
    ]

    operations = [

        migrations.AddField(
            model_name='source',
            name='live',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.RunPython(set_live, reverse_code=reset_live)

    ]
