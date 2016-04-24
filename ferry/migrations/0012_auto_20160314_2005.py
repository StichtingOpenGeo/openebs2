# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ferry', '0011_auto_20160313_1131'),
    ]

    operations = [
        migrations.AddField(
            model_name='ferrykv6messages',
            name='status_updated',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='ferrykv6messages',
            name='status',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Status', choices=[(1, 'Gereerd voor vertrek'), (5, 'Vertrokken'), (10, 'Aankomst')]),
        ),
    ]
