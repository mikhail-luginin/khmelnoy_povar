# Generated by Django 4.1 on 2023-05-19 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iiko', '0016_alter_supplier_is_revise'),
    ]

    operations = [
        migrations.AddField(
            model_name='storage',
            name='terminal_ids',
            field=models.JSONField(default=list, null=True),
        ),
    ]
