# Generated by Django 4.1 on 2023-05-08 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bar', '0004_rename_bonus_timetable_premium'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timetable',
            name='percnet',
        ),
        migrations.AddField(
            model_name='timetable',
            name='percent',
            field=models.IntegerField(default=0),
        ),
    ]
