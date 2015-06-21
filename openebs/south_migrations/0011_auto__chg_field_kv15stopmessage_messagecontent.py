# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Kv15Stopmessage.messagecontent'
        db.alter_column(u'openebs_kv15stopmessage', 'messagecontent', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

    def backwards(self, orm):

        # Changing field 'Kv15Stopmessage.messagecontent'
        db.alter_column(u'openebs_kv15stopmessage', 'messagecontent', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

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
        u'kv1.kv1journey': {
            'Meta': {'unique_together': "(('dataownercode', 'line', 'journeynumber', 'scheduleref'),)", 'object_name': 'Kv1Journey'},
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'departuretime': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'direction': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journeynumber': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '6'}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'journeys'", 'to': u"orm['kv1.Kv1Line']"}),
            'scheduleref': ('django.db.models.fields.PositiveIntegerField', [], {})
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
        },
        u'openebs.kv15log': {
            'Meta': {'object_name': 'Kv15Log'},
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipaddress': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'messagecodedate': ('django.db.models.fields.DateField', [], {}),
            'messagecodenumber': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '0'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'openebs.kv15messageline': {
            'Meta': {'unique_together': "([u'stopmessage', u'line'],)", 'object_name': 'Kv15MessageLine'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kv1.Kv1Line']"}),
            'stopmessage': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['openebs.Kv15Stopmessage']"})
        },
        u'openebs.kv15messagestop': {
            'Meta': {'unique_together': "([u'stopmessage', u'stop'],)", 'object_name': 'Kv15MessageStop'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stop': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'messages'", 'to': u"orm['kv1.Kv1Stop']"}),
            'stopmessage': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['openebs.Kv15Stopmessage']"})
        },
        u'openebs.kv15scenario': {
            'Meta': {'object_name': 'Kv15Scenario'},
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'openebs.kv15scenariomessage': {
            'Meta': {'object_name': 'Kv15ScenarioMessage'},
            'advicecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'advicetype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'effectcontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'effecttype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measurecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'measuretype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'messagecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'messagedurationtype': ('django.db.models.fields.CharField', [], {'default': "u'ENDTIME'", 'max_length': '10'}),
            'messagepriority': ('django.db.models.fields.CharField', [], {'default': "u'PTPROCESS'", 'max_length': '10'}),
            'messagetype': ('django.db.models.fields.CharField', [], {'default': "u'GENERAL'", 'max_length': '10'}),
            'reasoncontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'reasontype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'scenario': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'messages'", 'to': u"orm['openebs.Kv15Scenario']"}),
            'subadvicetype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'subeffecttype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'submeasuretype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'subreasontype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'openebs.kv15scenariostop': {
            'Meta': {'object_name': 'Kv15ScenarioStop'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'stops'", 'to': u"orm['openebs.Kv15ScenarioMessage']"}),
            'stop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kv1.Kv1Stop']"})
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
            'messagecodedate': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'messagecodenumber': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '0'}),
            'messagecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'messagedurationtype': ('django.db.models.fields.CharField', [], {'default': "u'ENDTIME'", 'max_length': '10'}),
            'messageendtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 6, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'messagepriority': ('django.db.models.fields.CharField', [], {'default': "u'PTPROCESS'", 'max_length': '10'}),
            'messagestarttime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'messagetimestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'messagetype': ('django.db.models.fields.CharField', [], {'default': "u'GENERAL'", 'max_length': '10'}),
            'reasoncontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'reasontype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'stops': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['kv1.Kv1Stop']", 'through': u"orm['openebs.Kv15MessageStop']", 'symmetrical': 'False'}),
            'subadvicetype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'subeffecttype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'submeasuretype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'subreasontype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'openebs.kv17change': {
            'Meta': {'unique_together': "((u'operatingday', u'line', u'journey', u'reinforcement'),)", 'object_name': 'Kv17Change'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_recovered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'journey': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'changes'", 'to': u"orm['kv1.Kv1Journey']"}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kv1.Kv1Line']"}),
            'operatingday': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'recovered': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'reinforcement': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'openebs.kv17journeychange': {
            'Meta': {'object_name': 'Kv17JourneyChange'},
            'advicecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'advicetype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'change': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'journey_details'", 'to': u"orm['openebs.Kv17Change']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reasoncontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'reasontype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'subadvicetype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'subreasontype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        u'openebs.kv17stopchange': {
            'Meta': {'object_name': 'Kv17StopChange'},
            'advicecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'advicetype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'change': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['openebs.Kv17Change']"}),
            'destinationcode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'destinationdetail16': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'destinationdisplay16': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'destinationname16': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'destinationname50': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lag': ('django.db.models.fields.IntegerField', [], {}),
            'reasoncontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'reasontype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'stop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kv1.Kv1Stop']"}),
            'stoporder': ('django.db.models.fields.IntegerField', [], {}),
            'stoptype': ('django.db.models.fields.CharField', [], {'default': "u'INTERMEDIATE'", 'max_length': '12'}),
            'subadvicetype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'subreasontype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'targetarrival': ('django.db.models.fields.DateTimeField', [], {}),
            'targetdeparture': ('django.db.models.fields.DateTimeField', [], {}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'openebs.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'company': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['openebs']