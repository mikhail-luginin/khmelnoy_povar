# Generated by Django 4.1 on 2023-06-03 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iiko', '0020_rename_sessions_session'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='close_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='session',
            name='open_date',
            field=models.DateField(),
        ),
    ]
