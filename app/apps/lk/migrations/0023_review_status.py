# Generated by Django 4.1 on 2023-06-05 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lk', '0022_rename_review_photo_review_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Создан'), (2, 'Закрыт')], default=1),
            preserve_default=False,
        ),
    ]
