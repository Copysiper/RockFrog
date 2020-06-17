# Generated by Django 2.2.5 on 2020-01-08 10:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0017_auto_20200108_1349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='groupname',
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name='group',
            name='pubdate',
            field=models.DateTimeField(default=datetime.datetime(2020, 1, 8, 13, 49, 29, 420517), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='grouparticle',
            name='pubdate',
            field=models.DateTimeField(default=datetime.datetime(2020, 1, 8, 13, 49, 29, 422518), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='groupcomment',
            name='pubdate',
            field=models.DateTimeField(default=datetime.datetime(2020, 1, 8, 13, 49, 29, 423519), verbose_name='date published'),
        ),
    ]