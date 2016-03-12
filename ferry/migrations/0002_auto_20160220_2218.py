# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ferry', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ferrykv6messages',
            name='delay',
            field=models.IntegerField(default=0),
        ),
    ]
