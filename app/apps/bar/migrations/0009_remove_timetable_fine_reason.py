# Generated by Django 4.1 on 2023-05-22 14:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bar', '0008_timetable_fine_reason'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timetable',
            name='fine_reason',
        ),
    ]