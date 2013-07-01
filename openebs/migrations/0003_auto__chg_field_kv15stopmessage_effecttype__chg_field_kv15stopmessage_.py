# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Kv15Stopmessage.effecttype'
        db.alter_column(u'openebs_kv15stopmessage', 'effecttype', self.gf('django.db.models.fields.SmallIntegerField')(null=True))

        # Changing field 'Kv15Stopmessage.reasontype'
        db.alter_column(u'openebs_kv15stopmessage', 'reasontype', self.gf('django.db.models.fields.SmallIntegerField')(null=True))

        # Changing field 'Kv15Stopmessage.measuretype'
        db.alter_column(u'openebs_kv15stopmessage', 'measuretype', self.gf('django.db.models.fields.SmallIntegerField')(null=True))

        # Changing field 'Kv15Stopmessage.advicetype'
        db.alter_column(u'openebs_kv15stopmessage', 'advicetype', self.gf('django.db.models.fields.SmallIntegerField')(null=True))

    def backwards(self, orm):

        # Changing field 'Kv15Stopmessage.effecttype'
        db.alter_column(u'openebs_kv15stopmessage', 'effecttype', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=0))

        # Changing field 'Kv15Stopmessage.reasontype'
        db.alter_column(u'openebs_kv15stopmessage', 'reasontype', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=0))

        # Changing field 'Kv15Stopmessage.measuretype'
        db.alter_column(u'openebs_kv15stopmessage', 'measuretype', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=0))

        # Changing field 'Kv15Stopmessage.advicetype'
        db.alter_column(u'openebs_kv15stopmessage', 'advicetype', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=0))

    models = {
        u'openebs.kv15log': {
            'Meta': {'object_name': 'Kv15Log'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipaddress': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'messagecodedate': ('django.db.models.fields.DateField', [], {}),
            'messagecodenumber': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '0'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'openebs.kv15schedule': {
            'Meta': {'object_name': 'Kv15Schedule'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'messageendtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'messagestarttime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'stopmessage': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['openebs.Kv15Stopmessage']"}),
            'weekdays': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'openebs.kv15stopmessage': {
            'Meta': {'object_name': 'Kv15Stopmessage'},
            'advicecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'advicetype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'effectcontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'effecttype': ('django.db.models.fields.SmallIntegerField', [], {'default': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isdeleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'measurecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'measuretype': ('django.db.models.fields.SmallIntegerField', [], {'default': '255', 'null': 'True', 'blank': 'True'}),
            'messagecodedate': ('django.db.models.fields.DateField', [], {}),
            'messagecodenumber': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '0'}),
            'messagecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'messagedurationtype': ('django.db.models.fields.CharField', [], {'default': "u'ENDTIME'", 'max_length': '10'}),
            'messageendtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'messagepriority': ('django.db.models.fields.CharField', [], {'default': "u'PTPROCESS'", 'max_length': '10'}),
            'messagescenario': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'messagestarttime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'messagetimestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'messagetype': ('django.db.models.fields.CharField', [], {'default': "u'GENERAL'", 'max_length': '10'}),
            'reasoncontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'reasontype': ('django.db.models.fields.SmallIntegerField', [], {'default': '255', 'null': 'True', 'blank': 'True'}),
            'subadvicetype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'subeffecttype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'submeasuretype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'subreasontype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        u'openebs.kv15stopmessagelineplanningnumber': {
            'Meta': {'object_name': 'Kv15StopmessageLineplanningnumber'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lineplanningnumber': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'stopmessage': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['openebs.Kv15Stopmessage']"})
        },
        u'openebs.kv15stopmessageuserstopcode': {
            'Meta': {'object_name': 'Kv15StopmessageUserstopcode'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stopmessage': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['openebs.Kv15Stopmessage']"}),
            'userstopcode': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['openebs']