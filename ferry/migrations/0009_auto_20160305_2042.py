# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ferry', '0008_auto_20160304_2133'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ferrykv6messages',
            name='departed',
        ),
        migrations.AddField(
            model_name='ferrykv6messages',
            name='full',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ferrykv6messages',
            name='status',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'INIT'), (5, b'DEPARTED'), (10, b'ARRIVED')]),
        ),
    ]
