# Generated by Django 4.1 on 2023-06-03 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iiko', '0023_session_date_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='close_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='session',
            name='open_date',
            field=models.DateTimeField(),
        ),
    ]
