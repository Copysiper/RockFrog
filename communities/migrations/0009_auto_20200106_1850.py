# Generated by Django 2.2.5 on 2020-01-06 15:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserProfile', '0002_auto_20191011_1604'),
        ('communities', '0008_auto_20200106_1845'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='admins',
            field=models.ManyToManyField(blank=True, related_name='admins', to='UserProfile.Profile'),
        ),
        migrations.AlterField(
            model_name='article',
            name='pubdate',
            field=models.DateTimeField(default=datetime.datetime(2020, 1, 6, 18, 50, 46, 14087), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='group',
            name='pubdate',
            field=models.DateTimeField(default=datetime.datetime(2020, 1, 6, 18, 50, 46, 12085), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='group',
            name='subscribers',
            field=models.ManyToManyField(blank=True, related_name='subscribers', to='UserProfile.Profile'),
        ),
    ]