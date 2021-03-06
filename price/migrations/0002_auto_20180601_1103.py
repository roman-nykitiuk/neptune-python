# Generated by Django 2.0.4 on 2018-06-01 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('price', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='discount',
            name='discount_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Discount by percent'), (2, 'Discount by money')], default=1, verbose_name='Discount type'),
        ),
        migrations.AlterField(
            model_name='discount',
            name='percent',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]
