# Generated by Django 2.0.4 on 2018-09-04 10:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0038_auto_20180828_0905'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('order', '0005_auto_20180904_0525'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='preference',
            unique_together={('client', 'content_type', 'object_id')},
        ),
    ]
