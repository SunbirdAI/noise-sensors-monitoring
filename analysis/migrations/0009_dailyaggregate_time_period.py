# Generated by Django 3.2.6 on 2022-11-11 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0008_auto_20221110_1940'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyaggregate',
            name='time_period',
            field=models.CharField(choices=[('daytime', 'Daytime'), ('nighttime', 'Nighttime')], default='daytime', max_length=10),
            preserve_default=False,
        ),
    ]
