# Generated by Django 4.1 on 2023-05-15 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iiko', '0015_alter_supplier_is_revise'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='is_revise',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Не привязан'), (1, 'Привязан')], default=0),
        ),
    ]
