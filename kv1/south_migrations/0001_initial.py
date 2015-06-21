# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Kv1Line'
        db.create_table(u'kv1_kv1line', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dataownercode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('lineplanningnumber', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('publiclinenumber', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('headsign', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('stop_map', self.gf('json_field.fields.JSONField')(default=u'null')),
        ))
        db.send_create_signal(u'kv1', ['Kv1Line'])

        # Adding unique constraint on 'Kv1Line', fields ['dataownercode', 'lineplanningnumber']
        db.create_unique(u'kv1_kv1line', ['dataownercode', 'lineplanningnumber'])

        # Adding model 'Kv1Stop'
        db.create_table(u'kv1_kv1stop', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userstopcode', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
            ('dataownercode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')()),
        ))
        db.send_create_signal(u'kv1', ['Kv1Stop'])


    def backwards(self, orm):
        # Removing unique constraint on 'Kv1Line', fields ['dataownercode', 'lineplanningnumber']
        db.delete_unique(u'kv1_kv1line', ['dataownercode', 'lineplanningnumber'])

        # Deleting model 'Kv1Line'
        db.delete_table(u'kv1_kv1line')

        # Deleting model 'Kv1Stop'
        db.delete_table(u'kv1_kv1stop')


    models = {
        u'kv1.kv1line': {
            'Meta': {'unique_together': "(('dataownercode', 'lineplanningnumber'),)", 'object_name': 'Kv1Line'},
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'headsign': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lineplanningnumber': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'publiclinenumber': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'stop_map': ('json_field.fields.JSONField', [], {'default': "u'null'"})
        },
        u'kv1.kv1stop': {
            'Meta': {'object_name': 'Kv1Stop'},
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'userstopcode': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'})
        }
    }

    complete_apps = ['kv1']