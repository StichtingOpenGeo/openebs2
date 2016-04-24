# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openebs', '0005_kv17change_is_cancel'),
        ('ferry', '0012_auto_20160314_2005'),
    ]

    operations = [
        migrations.AddField(
            model_name='ferryline',
            name='scenario_cancelled',
            field=models.ForeignKey(verbose_name="Scenario 'Boot uit vaart'", blank=True, to='openebs.Kv15Scenario', null=True),
        ),
    ]
