# Generated by Django 2.2.5 on 2020-01-07 06:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0012_auto_20200107_0906'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grouparticle',
            name='title',
        ),
        migrations.AlterField(
            model_name='group',
            name='pubdate',
            field=models.DateTimeField(default=datetime.datetime(2020, 1, 7, 9, 10, 56, 692845), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='grouparticle',
            name='pubdate',
            field=models.DateTimeField(default=datetime.datetime(2020, 1, 7, 9, 10, 56, 693846), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='groupcomment',
            name='pubdate',
            field=models.DateTimeField(default=datetime.datetime(2020, 1, 7, 9, 10, 56, 694847), verbose_name='date published'),
        ),
    ]
