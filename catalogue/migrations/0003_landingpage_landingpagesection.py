# -*- coding: utf-8 -*-


from django.db import models, migrations
import wagtail.core.fields
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0005_make_filter_spec_unique'),
        ('wagtailcore', '0010_change_page_owner_to_null_on_delete'),
        ('catalogue', '0002_auto_20150224_1844'),
    ]

    operations = [
        migrations.CreateModel(
            name='LandingPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, on_delete=models.CASCADE, serialize=False, to='wagtailcore.Page')),
                ('introduction', wagtail.core.fields.RichTextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', models.Model),
        ),
        migrations.CreateModel(
            name='LandingPageSection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('title', models.CharField(max_length=256)),
                ('abbreviation', models.CharField(max_length=32)),
                ('css_class', models.CharField(max_length=64)),
                ('introduction', wagtail.core.fields.RichTextField()),
                ('image', models.ForeignKey(to='wagtailimages.Image', on_delete=models.CASCADE,)),
                ('landing_page', modelcluster.fields.ParentalKey(related_name='sections', to='catalogue.LandingPage')),
                ('page', models.ForeignKey(to='wagtailcore.Page', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
