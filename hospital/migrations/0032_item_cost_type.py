# Generated by Django 2.0.4 on 2018-07-03 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0031_item_discounts'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='cost_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Unit cost'), (2, 'System cost')], default=1, verbose_name='Cost type'),
        ),
    ]