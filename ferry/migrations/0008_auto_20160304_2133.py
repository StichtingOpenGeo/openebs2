# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ferry', '0007_auto_20160304_1628'),
    ]

    operations = [
        migrations.AddField(
            model_name='ferrykv6messages',
            name='ferry',
            field=models.ForeignKey(default=1, to='ferry.FerryLine', on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='ferrykv6messages',
            unique_together=set([('ferry', 'journeynumber', 'operatingday')]),
        ),
        migrations.RemoveField(
            model_name='ferrykv6messages',
            name='line',
        ),
    ]
