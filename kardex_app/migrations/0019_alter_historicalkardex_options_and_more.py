# Generated by Django 4.1.2 on 2022-11-18 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kardex_app', '0018_historicalkardex_department_kardex_department'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historicalkardex',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical kardex', 'verbose_name_plural': 'historical kardexs'},
        ),
        migrations.AlterField(
            model_name='historicalkardex',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
    ]
