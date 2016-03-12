# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ferry', '0003_auto_20160220_2235'),
    ]

    operations = [
        migrations.AddField(
            model_name='ferrykv6messages',
            name='cancelled',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
