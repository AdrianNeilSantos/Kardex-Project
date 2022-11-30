# Generated by Django 4.1.2 on 2022-11-24 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("kardex_app", "0022_historicalkardex_case_num_kardex_case_num"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalkardex",
            name="condition",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="historicalkardex",
            name="diagnosis",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="kardex",
            name="condition",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="kardex",
            name="diagnosis",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]