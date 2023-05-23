# Generated by Django 4.1 on 2023-05-23 08:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lk', '0004_remove_jobplace_oklad_jobplace_gain_shift_oklad_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Кандидат'), (2, 'Стажер'), (3, 'Сотрудник'), (4, 'Резерв')], default=3),
        ),
        migrations.CreateModel(
            name='ItemDeficit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('item', models.CharField(max_length=128)),
                ('amount', models.CharField(max_length=32)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Создано'), (2, 'Отправлено'), (3, 'Получено')])),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='lk.profile')),
            ],
        ),
    ]