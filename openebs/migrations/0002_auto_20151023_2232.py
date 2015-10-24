# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openebs', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='kv1stopfilterstop',
            options={'verbose_name': 'Filter halte', 'verbose_name_plural': 'Filter haltes'},
        ),
        migrations.AlterField(
            model_name='kv1stopfilter',
            name='name',
            field=models.CharField(max_length=25, verbose_name='Naam'),
        ),
        migrations.AlterUniqueTogether(
            name='kv1stopfilterstop',
            unique_together=set([('filter', 'stop')]),
        ),
    ]
