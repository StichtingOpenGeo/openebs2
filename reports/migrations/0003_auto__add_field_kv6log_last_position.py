# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Kv6Log.last_position'
        db.add_column(u'reports_kv6log', 'last_position',
                      self.gf('django.contrib.gis.db.models.fields.PointField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Kv6Log.last_position'
        db.delete_column(u'reports_kv6log', 'last_position')


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
        }
    }

    complete_apps = ['reports']