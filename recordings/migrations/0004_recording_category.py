# Generated by Django 3.2.6 on 2022-03-09 07:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recordings', '0003_auto_20210831_1321'),
    ]

    operations = [
        migrations.AddField(
            model_name='recording',
            name='category',
            field=models.PositiveSmallIntegerField(null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(19)]),
        ),
    ]
