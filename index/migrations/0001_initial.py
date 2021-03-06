# Generated by Django 2.0.3 on 2018-04-08 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IpInterface',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ipaddr', models.GenericIPAddressField(verbose_name='分配的ip地址')),
                ('function', models.CharField(blank=True, max_length=20, null=True, verbose_name='ip对应的功能')),
                ('username', models.CharField(blank=True, max_length=20, null=True, verbose_name='用户名')),
                ('password', models.CharField(blank=True, max_length=20, null=True, verbose_name='对应的密码')),
                ('comment', models.CharField(blank=True, max_length=50, null=True, verbose_name='备注')),
            ],
            options={
                'verbose_name_plural': 'ip分配结果',
                'ordering': ['-ipaddr'],
            },
        ),
    ]
