# Generated by Django 4.1 on 2023-06-02 22:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iiko', '0019_sessions_storage'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Sessions',
            new_name='Session',
        ),
    ]