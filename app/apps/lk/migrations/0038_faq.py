# Generated by Django 4.1 on 2023-07-10 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lk', '0037_remove_employee_description_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField()),
            ],
        ),
    ]
