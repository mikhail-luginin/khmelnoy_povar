# Generated by Django 4.1 on 2023-05-24 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lk', '0008_alter_itemdeficit_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='photo',
            field=models.ImageField(upload_to='employee_photos'),
        ),
    ]
