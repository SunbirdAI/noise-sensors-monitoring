# Generated by Django 3.2.6 on 2022-02-23 12:55

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('devices', '0016_auto_20220208_1335'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyAnalysis',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('daily_avg_db_level', models.FloatField()),
                ('daily_max_db_level', models.FloatField()),
                ('daily_no_of_exceedances', models.FloatField()),
                ('device', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='devices.device')),
            ],
        ),
    ]