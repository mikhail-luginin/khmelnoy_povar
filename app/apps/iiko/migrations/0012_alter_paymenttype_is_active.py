# Generated by Django 4.1 on 2023-05-15 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iiko', '0011_alter_paymenttype_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymenttype',
            name='is_active',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Не активен'), (1, 'Активен')]),
        ),
    ]
