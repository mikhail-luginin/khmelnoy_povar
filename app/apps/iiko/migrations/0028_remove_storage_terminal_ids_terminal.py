# Generated by Django 4.1 on 2023-06-23 23:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iiko', '0027_alter_session_session_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='storage',
            name='terminal_ids',
        ),
        migrations.CreateModel(
            name='Terminal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('terminal_uuid', models.CharField(max_length=255)),
                ('storage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iiko.storage')),
            ],
        ),
    ]