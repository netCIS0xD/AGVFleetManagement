# Generated by Django 3.2.19 on 2025-01-12 21:01

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('remote_car', '0013_auto_20250112_2051'),
    ]

    operations = [
        migrations.AddField(
            model_name='envdata',
            name='AMRID',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='envdata',
            name='siteID',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='car',
            name='car_lastTimeConnected',
            field=models.TextField(default=datetime.datetime(2025, 1, 12, 21, 1, 49, 272094)),
        ),
    ]
