# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ferry', '0010_auto_20160305_2105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ferrykv6messages',
            name='delay',
            field=models.IntegerField(help_text='In seconden', null=True, verbose_name='Vertraging', blank=True),
        ),
        migrations.AlterField(
            model_name='ferryline',
            name='line',
            field=models.OneToOneField(verbose_name='Lijn', to='kv1.Kv1Line'),
        ),
    ]
