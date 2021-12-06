# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0004_impression_ocve_ac_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='impression',
            name='ocve_ac_code',
            field=models.CharField(max_length=128, null=True, verbose_name=b'AC Code in CFEO/OCVE', blank=True),
            preserve_default=True,
        ),
    ]
