# Generated by Django 4.1 on 2023-06-05 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lk', '0023_review_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='reviews',
            field=models.ManyToManyField(to='lk.review'),
        ),
        migrations.AlterField(
            model_name='review',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Создан'), (2, 'Закрыт')], default=1),
        ),
    ]
