# Generated by Django 4.1 on 2023-05-07 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bar', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramChats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.CharField(max_length=16)),
                ('name', models.CharField(max_length=32)),
            ],
        ),
    ]
