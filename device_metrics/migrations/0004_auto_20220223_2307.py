# Generated by Django 3.2.6 on 2022-02-23 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device_metrics', '0003_auto_20220217_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicemetrics',
            name='battery_voltage',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='devicemetrics',
            name='panel_voltage',
            field=models.FloatField(),
        ),
    ]
