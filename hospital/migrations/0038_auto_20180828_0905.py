# Generated by Django 2.0.4 on 2018-08-28 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0037_auto_20180824_0846'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='identifier',
            field=models.CharField(max_length=255, unique=True, verbose_name='Identifier number'),
        ),
    ]
