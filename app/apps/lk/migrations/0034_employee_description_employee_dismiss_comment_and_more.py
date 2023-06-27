# Generated by Django 4.1 on 2023-06-26 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lk', '0033_expensestatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='description',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='dismiss_comment',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='employee',
            name='status_change_comment',
            field=models.CharField(default='', max_length=255),
        ),
    ]
