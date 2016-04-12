# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openebs', '0005_kv17change_is_cancel'),
    ]

    operations = [
        migrations.CreateModel(
            name='Kv15ScenarioInstances',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.ForeignKey(to='openebs.Kv15Stopmessage')),
                ('scenario', models.ForeignKey(to='openebs.Kv15Scenario')),
            ],
        ),
    ]
