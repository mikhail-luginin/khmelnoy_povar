# Generated by Django 4.1 on 2023-06-22 08:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lk', '0032_rename_gain_shift_oklad_jobplace_gain_shift_oklad_accrual_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('success', models.BooleanField(choices=[(False, 'Отказ'), (True, 'Принят')])),
                ('comments', models.JSONField(default=list)),
                ('expense', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lk.expense')),
            ],
        ),
    ]
