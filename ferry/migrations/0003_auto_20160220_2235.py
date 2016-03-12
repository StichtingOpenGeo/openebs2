# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ferry', '0002_auto_20160220_2218'),
    ]

    operations = [
        migrations.AddField(
            model_name='ferrykv6messages',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 20, 21, 35, 31, 779583, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ferrykv6messages',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 20, 21, 35, 50, 349208, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
