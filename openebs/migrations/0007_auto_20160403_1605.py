# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openebs', '0006_kv15scenarioinstances'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Kv15ScenarioInstances',
            new_name='Kv15ScenarioInstance',
        ),
    ]
