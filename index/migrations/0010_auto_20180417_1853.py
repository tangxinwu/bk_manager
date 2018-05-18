# Generated by Django 2.0.3 on 2018-04-17 10:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0009_ipinterface_especily'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hardware',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hardware_type', models.CharField(blank=True, max_length=50, null=True, verbose_name='硬件类型')),
            ],
            options={
                'verbose_name_plural': '硬件类型',
                'ordering': ['-hardware_type'],
            },
        ),
        migrations.AddField(
            model_name='ipinterface',
            name='hardware_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='index.Hardware'),
        ),
    ]
