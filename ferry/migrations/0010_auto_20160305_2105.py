# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ferry', '0009_auto_20160305_2042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ferrykv6messages',
            name='cancelled',
            field=models.BooleanField(default=False, verbose_name='Opgeheven?'),
        ),
        migrations.AlterField(
            model_name='ferrykv6messages',
            name='delay',
            field=models.IntegerField(help_text='In seconden', verbose_name='Vertraging', blank=True),
        ),
        migrations.AlterField(
            model_name='ferrykv6messages',
            name='ferry',
            field=models.ForeignKey(verbose_name='Veerbootlijn', to='ferry.FerryLine'),
        ),
        migrations.AlterField(
            model_name='ferrykv6messages',
            name='full',
            field=models.BooleanField(default=False, verbose_name='Is vol?'),
        ),
        migrations.AlterField(
            model_name='ferrykv6messages',
            name='journeynumber',
            field=models.PositiveIntegerField(verbose_name='Ritnummer'),
        ),
        migrations.AlterField(
            model_name='ferrykv6messages',
            name='operatingday',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Dienstregelingsdatum'),
        ),
        migrations.AlterField(
            model_name='ferrykv6messages',
            name='status',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Status', choices=[(1, 'Gereerd voor vertrek'), (5, 'Vertrokken'), (10, 'Aankomst')]),
        ),
        migrations.AlterField(
            model_name='ferryline',
            name='line',
            field=models.ForeignKey(verbose_name='Lijn', to='kv1.Kv1Line', unique=True),
        ),
        migrations.AlterField(
            model_name='ferryline',
            name='stop_arrival',
            field=models.ForeignKey(related_name='ferry_arrival', verbose_name='Aankomstpunt', to='kv1.Kv1Stop'),
        ),
        migrations.AlterField(
            model_name='ferryline',
            name='stop_depart',
            field=models.ForeignKey(related_name='ferry_departure', verbose_name='Vertrekpunt', to='kv1.Kv1Stop'),
        ),
    ]
