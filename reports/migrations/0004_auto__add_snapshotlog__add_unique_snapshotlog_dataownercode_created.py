# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SnapshotLog'
        db.create_table(u'reports_snapshotlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dataownercode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('data', self.gf('json_field.fields.JSONField')(default=u'null')),
        ))
        db.send_create_signal(u'reports', ['SnapshotLog'])

        # Adding unique constraint on 'SnapshotLog', fields ['dataownercode', 'created']
        db.create_unique(u'reports_snapshotlog', ['dataownercode', 'created'])


    def backwards(self, orm):
        # Removing unique constraint on 'SnapshotLog', fields ['dataownercode', 'created']
        db.delete_unique(u'reports_snapshotlog', ['dataownercode', 'created'])

        # Deleting model 'SnapshotLog'
        db.delete_table(u'reports_snapshotlog')


    models = {
        u'reports.kv6log': {
            'Meta': {'unique_together': "(('dataownercode', 'lineplanningnumber', 'journeynumber', 'operatingday'),)", 'object_name': 'Kv6Log'},
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journeynumber': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '6'}),
            'last_logged': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'last_position': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'last_punctuality': ('django.db.models.fields.IntegerField', [], {}),
            'lineplanningnumber': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'max_punctuality': ('django.db.models.fields.IntegerField', [], {}),
            'operatingday': ('django.db.models.fields.DateField', [], {}),
            'vehiclenumber': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        u'reports.snapshotlog': {
            'Meta': {'unique_together': "(('dataownercode', 'created'),)", 'object_name': 'SnapshotLog'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'data': ('json_field.fields.JSONField', [], {'default': "u'null'"}),
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['reports']