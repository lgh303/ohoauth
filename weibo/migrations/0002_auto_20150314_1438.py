# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('weibo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='expires_in',
            field=models.CharField(default=datetime.datetime(2015, 3, 14, 6, 38, 1, 893123, tzinfo=utc), max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='rtime',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 14, 6, 38, 13, 673827, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='uid',
            field=models.CharField(unique=True, max_length=20),
            preserve_default=True,
        ),
    ]
