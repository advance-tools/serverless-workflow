# Generated by Django 3.1.7 on 2021-07-29 12:05

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='buffer_immediate_next',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.JSONField(null=True), null=True, size=None),
        ),
        migrations.AddField(
            model_name='task',
            name='buffer_sub_task_next',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.JSONField(null=True), null=True, size=None),
        ),
    ]
