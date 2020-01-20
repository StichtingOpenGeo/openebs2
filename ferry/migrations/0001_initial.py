# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('kv1', '0002_kv1line_is_ferry'),
    ]

    operations = [
        migrations.CreateModel(
            name='FerryKv6Messages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('operatingday', models.DateField(default=django.utils.timezone.now)),
                ('journeynumber', models.PositiveIntegerField()),
                ('delay', models.IntegerField()),
                ('departed', models.BooleanField()),
                ('line', models.ForeignKey(to='kv1.Kv1Line', on_delete=models.CASCADE)),
            ],
        ),
    ]
