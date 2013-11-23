# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Kv1JourneyStop'
        db.create_table(u'kv1_kv1journeystop', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('journey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kv1.Kv1Journey'])),
            ('stop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kv1.Kv1Stop'])),
            ('stoporder', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('stoptype', self.gf('django.db.models.fields.CharField')(default='INTERMEDIATE', max_length=12)),
            ('scheduledarrival', self.gf('django.db.models.fields.TimeField')()),
            ('scheduleddeparture', self.gf('django.db.models.fields.TimeField')()),
        ))
        db.send_create_signal(u'kv1', ['Kv1JourneyStop'])

        # Adding unique constraint on 'Kv1JourneyStop', fields ['journey', 'stop']
        db.create_unique(u'kv1_kv1journeystop', ['journey_id', 'stop_id'])

        # Adding unique constraint on 'Kv1JourneyStop', fields ['journey', 'stoporder']
        db.create_unique(u'kv1_kv1journeystop', ['journey_id', 'stoporder'])

        # Adding model 'Kv1Journey'
        db.create_table(u'kv1_kv1journey', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dataownercode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('line', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kv1.Kv1Line'])),
            ('journeynumber', self.gf('django.db.models.fields.PositiveIntegerField')(max_length=6)),
            ('date_start', self.gf('django.db.models.fields.DateField')()),
            ('date_end', self.gf('django.db.models.fields.DateField')()),
            ('day_monday', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('day_tuesday', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('day_wednesday', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('day_thursday', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('day_friday', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('day_saturday', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('day_sunday', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'kv1', ['Kv1Journey'])

        # Adding unique constraint on 'Kv1Journey', fields ['dataownercode', 'journeynumber']
        db.create_unique(u'kv1_kv1journey', ['dataownercode', 'journeynumber'])


    def backwards(self, orm):
        # Removing unique constraint on 'Kv1Journey', fields ['dataownercode', 'journeynumber']
        db.delete_unique(u'kv1_kv1journey', ['dataownercode', 'journeynumber'])

        # Removing unique constraint on 'Kv1JourneyStop', fields ['journey', 'stoporder']
        db.delete_unique(u'kv1_kv1journeystop', ['journey_id', 'stoporder'])

        # Removing unique constraint on 'Kv1JourneyStop', fields ['journey', 'stop']
        db.delete_unique(u'kv1_kv1journeystop', ['journey_id', 'stop_id'])

        # Deleting model 'Kv1JourneyStop'
        db.delete_table(u'kv1_kv1journeystop')

        # Deleting model 'Kv1Journey'
        db.delete_table(u'kv1_kv1journey')


    models = {
        u'kv1.kv1journey': {
            'Meta': {'unique_together': "(('dataownercode', 'journeynumber'),)", 'object_name': 'Kv1Journey'},
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'date_end': ('django.db.models.fields.DateField', [], {}),
            'date_start': ('django.db.models.fields.DateField', [], {}),
            'day_friday': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'day_monday': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'day_saturday': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'day_sunday': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'day_thursday': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'day_tuesday': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'day_wednesday': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journeynumber': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '6'}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kv1.Kv1Line']"})
        },
        u'kv1.kv1journeystop': {
            'Meta': {'unique_together': "(('journey', 'stop'), ('journey', 'stoporder'))", 'object_name': 'Kv1JourneyStop'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kv1.Kv1Journey']"}),
            'scheduledarrival': ('django.db.models.fields.TimeField', [], {}),
            'scheduleddeparture': ('django.db.models.fields.TimeField', [], {}),
            'stop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kv1.Kv1Stop']"}),
            'stoporder': ('django.db.models.fields.SmallIntegerField', [], {}),
            'stoptype': ('django.db.models.fields.CharField', [], {'default': "'INTERMEDIATE'", 'max_length': '12'})
        },
        u'kv1.kv1line': {
            'Meta': {'unique_together': "(('dataownercode', 'lineplanningnumber'),)", 'object_name': 'Kv1Line'},
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'headsign': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lineplanningnumber': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'publiclinenumber': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'stop_map': ('json_field.fields.JSONField', [], {'default': "u'null'"})
        },
        u'kv1.kv1stop': {
            'Meta': {'unique_together': "(('dataownercode', 'userstopcode'),)", 'object_name': 'Kv1Stop'},
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'userstopcode': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['kv1']