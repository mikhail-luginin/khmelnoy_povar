# Generated by Django 4.1 on 2023-06-09 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lk', '0030_itemdeficit_sended_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemdeficit',
            name='arrived_amount',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='itemdeficit',
            name='sended_amount',
            field=models.CharField(max_length=255, null=True),
        ),
    ]