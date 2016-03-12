# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openebs', '0003_auto_20151024_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kv17stopchange',
            name='change',
            field=models.ForeignKey(related_name='stop_change', to='openebs.Kv17Change'),
        ),
        migrations.AlterField(
            model_name='kv17stopchange',
            name='lag',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='kv17stopchange',
            name='stoptype',
            field=models.CharField(default='INTERMEDIATE', max_length=12, null=True, blank=True, choices=[(b'FIRST', b'Beginhalte'), (b'INTERMEDIATE', b'Tussenhalte'), (b'LAST', b'Eindhalte')]),
        ),
        migrations.AlterField(
            model_name='kv17stopchange',
            name='targetarrival',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='kv17stopchange',
            name='targetdeparture',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
