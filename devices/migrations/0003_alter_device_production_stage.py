# Generated by Django 3.2.6 on 2021-08-06 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0002_auto_20210806_1210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='production_stage',
            field=models.CharField(choices=[('Deployed', 'Deployed'), ('Testing', 'Testing'), ('Recalled', 'Recalled'), ('Fixing', 'Fixing')], default='Testing', max_length=50),
        ),
    ]
