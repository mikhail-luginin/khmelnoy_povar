# Generated by Django 4.1 on 2023-05-07 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bar', '0002_telegramchats'),
    ]

    operations = [
        migrations.AddField(
            model_name='timetable',
            name='bonus',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='timetable',
            name='fine',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='timetable',
            name='percnet',
            field=models.FloatField(default=0, null=True),
        ),
    ]