# Generated by Django 3.2.10 on 2022-02-09 06:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task_services', '0002_task_unique_user-code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='buffer_immediate_next',
        ),
        migrations.RemoveField(
            model_name='task',
            name='buffer_sub_task_next',
        ),
    ]
