# Generated by Django 3.0.4 on 2020-05-24 16:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0018_auto_20200524_1654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='not_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 24, 19, 45, 31, 333599), verbose_name='date published'),
        ),
    ]