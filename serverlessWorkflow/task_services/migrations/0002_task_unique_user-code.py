# Generated by Django 3.2.10 on 2022-01-19 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_services', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='task',
            constraint=models.UniqueConstraint(fields=('my_user', 'code'), name='Unique_User-Code'),
        ),
    ]