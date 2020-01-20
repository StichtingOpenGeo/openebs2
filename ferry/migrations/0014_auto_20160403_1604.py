# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ferry', '0013_ferryline_scenario_cancelled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ferryline',
            name='scenario_cancelled',
            field=models.ForeignKey(verbose_name="Scenario 'Dienst uit vaart'", blank=True, to='openebs.Kv15Scenario', null=True, on_delete=models.CASCADE),
        ),
    ]
