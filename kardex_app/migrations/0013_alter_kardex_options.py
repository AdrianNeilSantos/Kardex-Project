# Generated by Django 4.1.2 on 2022-11-02 08:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kardex_app', '0012_alter_historicalkardex_extra_field_values_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='kardex',
            options={'ordering': ['-date_time', '-date_added']},
        ),
    ]
