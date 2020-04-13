# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ferry', '0006_auto_20160304_1625'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ferryline',
            options={'verbose_name': 'Ferry', 'verbose_name_plural': 'Ferries'},
        ),
        migrations.AlterField(
            model_name='ferryline',
            name='line',
            field=models.ForeignKey(to='kv1.Kv1Line', unique=True, on_delete=models.CASCADE),
        ),
    ]
