# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName". 
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'openebs.kv15log': {
            'Meta': {'object_name': 'Kv15Log'},
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipaddress': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'messagecodedate': ('django.db.models.fields.DateField', [], {}),
            'messagecodenumber': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '0'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'openebs.kv15scenario': {
            'Meta': {'object_name': 'Kv15Scenario'},
            'advicecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'advicetype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'effectcontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'effecttype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measurecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'measuretype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'messagecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'messagedurationtype': ('django.db.models.fields.CharField', [], {'default': "u'ENDTIME'", 'max_length': '10'}),
            'messageendtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'messagepriority': ('django.db.models.fields.CharField', [], {'default': "u'PTPROCESS'", 'max_length': '10'}),
            'messagestarttime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'messagetimestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'messagetype': ('django.db.models.fields.CharField', [], {'default': "u'GENERAL'", 'max_length': '10'}),
            'reasoncontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'reasontype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'scenario': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'subadvicetype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'subeffecttype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'submeasuretype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'subreasontype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
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
            'Meta': {'unique_together': "((u'dataownercode', u'messagecodedate', u'messagecodenumber'),)", 'object_name': 'Kv15Stopmessage'},
            'advicecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'advicetype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'effectcontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'effecttype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isdeleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'measurecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'measuretype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'messagecodedate': ('django.db.models.fields.DateField', [], {}),
            'messagecodenumber': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '0'}),
            'messagecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'messagedurationtype': ('django.db.models.fields.CharField', [], {'default': "u'ENDTIME'", 'max_length': '10'}),
            'messageendtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'messagepriority': ('django.db.models.fields.CharField', [], {'default': "u'PTPROCESS'", 'max_length': '10'}),
            'messagestarttime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'messagetimestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'messagetype': ('django.db.models.fields.CharField', [], {'default': "u'GENERAL'", 'max_length': '10'}),
            'reasoncontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'reasontype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'subadvicetype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'subeffecttype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'submeasuretype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'subreasontype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
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
        },
        u'openebs.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'company': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['contenttypes', 'auth', 'openebs']
    symmetrical = True
