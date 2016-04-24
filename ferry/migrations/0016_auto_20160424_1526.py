# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ferry', '0015_ferryline_enable_auto_messages'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ferrykv6messages',
            options={'verbose_name': 'Afvaart', 'verbose_name_plural': 'Afvaarten'},
        ),
        migrations.AlterModelOptions(
            name='ferryline',
            options={'verbose_name': 'Veerboot', 'verbose_name_plural': 'Veerboten'},
        ),
    ]
