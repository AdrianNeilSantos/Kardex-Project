# Generated by Django 4.1.2 on 2022-11-20 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kardex_app', '0019_alter_historicalkardex_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historicalkardex',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical kardex'},
        ),
        migrations.AlterField(
            model_name='historicalkardex',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='nurse',
            name='sex',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]