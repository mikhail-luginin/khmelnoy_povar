# Generated by Django 4.1 on 2023-05-18 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lk', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Кандидат'), (2, 'Стажер'), (3, 'Сотрудник')], default=3),
        ),
    ]