# Generated by Django 3.2.6 on 2024-07-17 18:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0020_remove_device_lastseen'),
        ('device_metrics', '0004_auto_20220223_2307'),
    ]

    operations = [
        migrations.CreateModel(
            name='SoundInferenceData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inference_probability', models.FloatField(default=0.0, help_text='Probability of predicted class')),
                ('inference_class', models.CharField(help_text='Name of predicted class', max_length=255)),
                ('inferred_audio_name', models.CharField(help_text='Name of inferred sound file', max_length=255)),
                ('device', models.ForeignKey(help_text='Device ID', on_delete=django.db.models.deletion.CASCADE, related_name='inferences', related_query_name='sound_data', to='devices.device')),
            ],
            options={
                'verbose_name_plural': 'Sound Inference Data',
            },
        ),
        migrations.CreateModel(
            name='EnvironmentalParameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temperature', models.FloatField(default=0.0, help_text='Environmental temperature')),
                ('pressure', models.FloatField(default=0.0, help_text='Atmospheric pressure')),
                ('humidity', models.FloatField(default=0.0, help_text='Atmospheric humidity')),
                ('air_quality', models.FloatField(default=0.0, help_text='Volatile organic compounds vary resistance')),
                ('ram_value', models.FloatField(default=0.0, help_text='Memory usage of the PI')),
                ('system_temperature', models.FloatField(default=0.0, help_text='Temperature of the PI')),
                ('power_usage', models.FloatField(default=0.0, help_text='Power utilization of the PI')),
                ('device', models.ForeignKey(help_text='Device ID', on_delete=django.db.models.deletion.CASCADE, related_name='environmental_parameters', related_query_name='environmental_param', to='devices.device')),
            ],
        ),
    ]
