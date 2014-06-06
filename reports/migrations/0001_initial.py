# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Kv6Log'
        db.create_table(u'reports_kv6log', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dataownercode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('lineplanningnumber', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('journeynumber', self.gf('django.db.models.fields.PositiveIntegerField')(max_length=6)),
            ('operatingday', self.gf('django.db.models.fields.DateField')()),
            ('last_punctuality', self.gf('django.db.models.fields.IntegerField')()),
            ('max_punctuality', self.gf('django.db.models.fields.IntegerField')()),
            ('last_logged', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'reports', ['Kv6Log'])

        # Adding unique constraint on 'Kv6Log', fields ['dataownercode', 'lineplanningnumber', 'journeynumber', 'operatingday']
        db.create_unique(u'reports_kv6log', ['dataownercode', 'lineplanningnumber', 'journeynumber', 'operatingday'])


    def backwards(self, orm):
        # Removing unique constraint on 'Kv6Log', fields ['dataownercode', 'lineplanningnumber', 'journeynumber', 'operatingday']
        db.delete_unique(u'reports_kv6log', ['dataownercode', 'lineplanningnumber', 'journeynumber', 'operatingday'])

        # Deleting model 'Kv6Log'
        db.delete_table(u'reports_kv6log')


    models = {
        u'reports.kv6log': {
            'Meta': {'unique_together': "(('dataownercode', 'lineplanningnumber', 'journeynumber', 'operatingday'),)", 'object_name': 'Kv6Log'},
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journeynumber': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '6'}),
            'last_logged': ('django.db.models.fields.DateTimeField', [], {}),
            'last_punctuality': ('django.db.models.fields.IntegerField', [], {}),
            'lineplanningnumber': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'max_punctuality': ('django.db.models.fields.IntegerField', [], {}),
            'operatingday': ('django.db.models.fields.DateField', [], {})
        }
    }

    complete_apps = ['reports']