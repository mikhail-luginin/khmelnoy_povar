# Generated by Django 4.1 on 2023-06-03 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iiko', '0024_alter_session_close_date_alter_session_open_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='close_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='open_date',
            field=models.DateTimeField(null=True),
        ),
    ]