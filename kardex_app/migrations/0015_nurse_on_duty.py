# Generated by Django 4.1.2 on 2022-11-06 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kardex_app', '0014_nurse_nurse_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='nurse',
            name='on_duty',
            field=models.CharField(blank=True, max_length=69, null=True),
        ),
    ]
