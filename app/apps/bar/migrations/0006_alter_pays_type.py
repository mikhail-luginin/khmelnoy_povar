# Generated by Django 4.1 on 2023-05-18 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bar', '0005_remove_timetable_percnet_timetable_percent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pays',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Внесение'), (2, 'Изъятие'), (4, 'Закупщик'), (5, 'Масло')]),
        ),
    ]
