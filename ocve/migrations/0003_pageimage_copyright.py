# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocve', '0002_annotation_geometry'),
    ]

    operations = [
        migrations.AddField(
            model_name='pageimage',
            name='copyright',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
