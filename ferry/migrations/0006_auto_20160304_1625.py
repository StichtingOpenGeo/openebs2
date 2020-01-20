# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kv1', '0003_remove_kv1line_is_ferry'),
        ('ferry', '0005_auto_20160221_1520'),
    ]

    operations = [
        migrations.CreateModel(
            name='FerryLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('line', models.ForeignKey(to='kv1.Kv1Line', on_delete=models.CASCADE)),
                ('stop_arrival', models.ForeignKey(related_name='ferry_arrival', to='kv1.Kv1Stop', on_delete=models.CASCADE)),
                ('stop_depart', models.ForeignKey(related_name='ferry_departure', to='kv1.Kv1Stop', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AlterField(
            model_name='ferrykv6messages',
            name='cancelled',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='ferrykv6messages',
            name='departed',
            field=models.BooleanField(default=False),
        ),
    ]
