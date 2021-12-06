# -*- coding: utf-8 -*-


from django.db import models, migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advert',
            name='rubric',
            field=wagtail.core.fields.RichTextField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stp',
            name='rubric',
            field=wagtail.core.fields.RichTextField(),
            preserve_default=True,
        ),
    ]
