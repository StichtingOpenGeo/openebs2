# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kv1', '0002_kv1line_is_ferry'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kv1line',
            name='is_ferry',
        ),
    ]
