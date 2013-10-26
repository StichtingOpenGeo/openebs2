# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Kv1Line.headsign'
        db.alter_column(u'kv1_kv1line', 'headsign', self.gf('django.db.models.fields.CharField')(max_length=100))

    def backwards(self, orm):

        # Changing field 'Kv1Line.headsign'
        db.alter_column(u'kv1_kv1line', 'headsign', self.gf('django.db.models.fields.CharField')(max_length=10))

    models = {
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
            'Meta': {'object_name': 'Kv1Stop'},
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'userstopcode': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'})
        }
    }

    complete_apps = ['kv1']