# Generated by Django 2.0.4 on 2018-06-25 03:58

from django.db import migrations, models
import functools
import neptune.utils


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0027_auto_20180622_0815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=functools.partial(neptune.utils.make_imagefield_filepath, *('clients',), **{})),
        ),
    ]