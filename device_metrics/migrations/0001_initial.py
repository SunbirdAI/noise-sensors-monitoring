# Generated by Django 3.2.6 on 2021-12-16 06:09

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('devices', '0011_auto_20210831_1913'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceMetrics',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('sig_strength', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(31)])),
                ('db_level', models.PositiveIntegerField()),
                ('last_rec', models.PositiveIntegerField()),
                ('last_upl', models.PositiveIntegerField()),
                ('panel_voltage', models.PositiveIntegerField()),
                ('battery_voltage', models.PositiveIntegerField()),
                ('data_balance', models.PositiveIntegerField()),
                ('datetime_uploaded', models.DateTimeField(auto_now_add=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='devices.device')),
            ],
        ),
    ]
