# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ferry', '0004_ferrykv6messages_cancelled'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ferrykv6messages',
            options={'verbose_name': 'Ferry journey', 'verbose_name_plural': 'Ferry journeys'},
        ),
        migrations.AlterUniqueTogether(
            name='ferrykv6messages',
            unique_together=set([('line', 'journeynumber', 'operatingday')]),
        ),
    ]
