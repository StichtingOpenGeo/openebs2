# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openebs', '0004_auto_20160305_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='kv17change',
            name='is_cancel',
            field=models.BooleanField(default=True, help_text='Rit kan ook een toelichting zijn voor een halte', verbose_name='Opgeheven?'),
        ),
    ]
