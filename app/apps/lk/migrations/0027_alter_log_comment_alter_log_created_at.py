# Generated by Django 4.1 on 2023-06-06 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lk', '0026_rename_logs_log'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='comment',
            field=models.CharField(default=None, max_length=128),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='log',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]