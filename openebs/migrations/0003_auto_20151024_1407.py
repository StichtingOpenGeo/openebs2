# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openebs', '0002_auto_20151023_2232'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='kv1stopfilter',
            options={'verbose_name': 'Filter', 'verbose_name_plural': 'Filters', 'permissions': (('edit_filters', 'Filters bewerken'),)},
        ),
        migrations.AlterModelOptions(
            name='kv1stopfilterstop',
            options={'ordering': ['stop__name', 'stop__timingpointcode'], 'verbose_name': 'Filter halte', 'verbose_name_plural': 'Filter haltes'},
        ),
    ]
