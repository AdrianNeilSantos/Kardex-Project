# Generated by Django 4.1.2 on 2022-10-18 14:08

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kardex_app', '0004_rename_datetime_kardex_date_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='kardex',
            name='labelMarkers',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=255, null=True), null=True, size=None),
        ),
        migrations.AddField(
            model_name='kardex',
            name='labelValues',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=255, null=True), null=True, size=None),
        ),
    ]
