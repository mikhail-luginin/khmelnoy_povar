# Generated by Django 4.1 on 2023-05-08 10:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bar', '0003_timetable_bonus_timetable_fine_timetable_percnet'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timetable',
            old_name='bonus',
            new_name='premium',
        ),
    ]