# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kv1', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='kv1line',
            name='is_ferry',
            field=models.BooleanField(default=False),
        ),
    ]
