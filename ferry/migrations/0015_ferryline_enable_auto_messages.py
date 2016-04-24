# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ferry', '0014_auto_20160403_1604'),
    ]

    operations = [
        migrations.AddField(
            model_name='ferryline',
            name='enable_auto_messages',
            field=models.BooleanField(default=False, verbose_name='Verstuur automatisch KV6 berichten'),
        ),
    ]
