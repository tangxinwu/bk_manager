# Generated by Django 2.0.5 on 2018-06-06 02:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0012_auto_20180528_1138'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='snapshottask',
            name='created_time',
        ),
        migrations.RemoveField(
            model_name='snapshottask',
            name='frequency',
        ),
    ]
