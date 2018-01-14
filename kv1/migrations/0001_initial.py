# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import jsonfield
from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Kv1Journey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dataownercode', models.CharField(max_length=10, choices=[(b'ARR', b'Arriva'), (b'VTN', b'Veolia'), (b'CXX', b'Connexxion'), (b'EBS', b'EBS'), (b'GVB', b'GVB'), (b'HTM', b'HTM'), (b'NS', b'Nederlandse Spoorwegen'), (b'RET', b'RET'), (b'SYNTUS', b'Syntus'), (b'QBUZZ', b'Qbuzz'), (b'TCR', b'Taxi Centrale Renesse'), (b'GOVI', b'GOVI')])),
                ('journeynumber', models.PositiveIntegerField()),
                ('scheduleref', models.PositiveIntegerField()),
                ('departuretime', models.PositiveIntegerField()),
                ('direction', models.PositiveSmallIntegerField()),
            ],
            options={
                'verbose_name': 'Rit',
                'verbose_name_plural': 'Ritinformatie',
            },
        ),
        migrations.CreateModel(
            name='Kv1JourneyDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('journey', models.ForeignKey(related_name='dates', to='kv1.Kv1Journey')),
            ],
            options={
                'verbose_name': 'Ritdag',
                'verbose_name_plural': 'Ritdag',
            },
        ),
        migrations.CreateModel(
            name='Kv1JourneyStop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stoporder', models.SmallIntegerField()),
                ('stoptype', models.CharField(default=b'INTERMEDIATE', max_length=12, choices=[(b'FIRST', b'Beginhalte'), (b'INTERMEDIATE', b'Tussenhalte'), (b'LAST', b'Eindhalte')])),
                ('targetarrival', models.TimeField()),
                ('targetdeparture', models.TimeField()),
                ('journey', models.ForeignKey(related_name='stops', to='kv1.Kv1Journey')),
            ],
            options={
                'verbose_name': 'Rithalte',
                'verbose_name_plural': 'Rithaltes',
            },
        ),
        migrations.CreateModel(
            name='Kv1Line',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dataownercode', models.CharField(max_length=10, choices=[(b'ARR', b'Arriva'), (b'VTN', b'Veolia'), (b'CXX', b'Connexxion'), (b'EBS', b'EBS'), (b'GVB', b'GVB'), (b'HTM', b'HTM'), (b'NS', b'Nederlandse Spoorwegen'), (b'RET', b'RET'), (b'SYNTUS', b'Syntus'), (b'QBUZZ', b'Qbuzz'), (b'TCR', b'Taxi Centrale Renesse'), (b'GOVI', b'GOVI')])),
                ('lineplanningnumber', models.CharField(max_length=10)),
                ('publiclinenumber', models.CharField(max_length=10)),
                ('headsign', models.CharField(max_length=100)),
                ('stop_map', jsonfield.JSONField(default='null', help_text='Enter a valid JSON object')),
            ],
            options={
                'verbose_name': 'Lijn',
                'verbose_name_plural': 'Lijninformatie',
            },
        ),
        migrations.CreateModel(
            name='Kv1Stop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('userstopcode', models.CharField(max_length=10)),
                ('dataownercode', models.CharField(max_length=10, choices=[(b'ARR', b'Arriva'), (b'VTN', b'Veolia'), (b'CXX', b'Connexxion'), (b'EBS', b'EBS'), (b'GVB', b'GVB'), (b'HTM', b'HTM'), (b'NS', b'Nederlandse Spoorwegen'), (b'RET', b'RET'), (b'SYNTUS', b'Syntus'), (b'QBUZZ', b'Qbuzz'), (b'TCR', b'Taxi Centrale Renesse'), (b'GOVI', b'GOVI')])),
                ('timingpointcode', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=50)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            options={
                'verbose_name': 'Halte',
                'verbose_name_plural': 'Halteinformatie',
            },
        ),
        migrations.AlterUniqueTogether(
            name='kv1stop',
            unique_together=set([('dataownercode', 'userstopcode')]),
        ),
        migrations.AlterUniqueTogether(
            name='kv1line',
            unique_together=set([('dataownercode', 'lineplanningnumber')]),
        ),
        migrations.AddField(
            model_name='kv1journeystop',
            name='stop',
            field=models.ForeignKey(to='kv1.Kv1Stop'),
        ),
        migrations.AddField(
            model_name='kv1journey',
            name='line',
            field=models.ForeignKey(related_name='journeys', to='kv1.Kv1Line'),
        ),
        migrations.AlterUniqueTogether(
            name='kv1journeystop',
            unique_together=set([('journey', 'stoporder'), ('journey', 'stop')]),
        ),
        migrations.AlterUniqueTogether(
            name='kv1journeydate',
            unique_together=set([('journey', 'date')]),
        ),
        migrations.AlterUniqueTogether(
            name='kv1journey',
            unique_together=set([('dataownercode', 'line', 'journeynumber', 'scheduleref')]),
        ),
    ]
