# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Kv17Change'
        db.create_table(u'openebs_kv17change', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dataownercode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('operatingday', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
            ('line', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kv1.Kv1Line'])),
            ('journey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kv1.Kv1Journey'])),
            ('reinforcement', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'openebs', ['Kv17Change'])

        # Adding model 'Kv17StopChange'
        db.create_table(u'openebs_kv17stopchange', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('change', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openebs.Kv17Change'])),
            ('type', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('stop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kv1.Kv1Stop'])),
            ('stoporder', self.gf('django.db.models.fields.IntegerField')()),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('lag', self.gf('django.db.models.fields.IntegerField')()),
            ('targetarrival', self.gf('django.db.models.fields.DateTimeField')()),
            ('targetdeparture', self.gf('django.db.models.fields.DateTimeField')()),
            ('stoptype', self.gf('django.db.models.fields.CharField')(default=u'INTERMEDIATE', max_length=12)),
            ('destinationcode', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('destinationname50', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('destinationname16', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('destinationdetail16', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('destinationdisplay16', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('reasontype', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('subreasontype', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('reasoncontent', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('advicetype', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('subadvicetype', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('advicecontent', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'openebs', ['Kv17StopChange'])

        # Adding model 'Kv17JourneyChange'
        db.create_table(u'openebs_kv17journeychange', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('change', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openebs.Kv17Change'])),
            ('is_recovered', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('reasontype', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('subreasontype', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('reasoncontent', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('advicetype', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('subadvicetype', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('advicecontent', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'openebs', ['Kv17JourneyChange'])


    def backwards(self, orm):
        # Deleting model 'Kv17Change'
        db.delete_table(u'openebs_kv17change')

        # Deleting model 'Kv17StopChange'
        db.delete_table(u'openebs_kv17stopchange')

        # Deleting model 'Kv17JourneyChange'
        db.delete_table(u'openebs_kv17journeychange')


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
            'scenario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['openebs.Kv15Scenario']"}),
            'subadvicetype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'subeffecttype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'submeasuretype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'subreasontype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'openebs.kv15scenariostop': {
            'Meta': {'object_name': 'Kv15ScenarioStop'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['openebs.Kv15ScenarioMessage']"}),
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
            'messagecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'messagedurationtype': ('django.db.models.fields.CharField', [], {'default': "u'ENDTIME'", 'max_length': '10'}),
            'messageendtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 11, 24, 0, 0)', 'null': 'True', 'blank': 'True'}),
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
            'Meta': {'object_name': 'Kv17Change'},
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kv1.Kv1Journey']"}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kv1.Kv1Line']"}),
            'operatingday': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'reinforcement': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'openebs.kv17journeychange': {
            'Meta': {'object_name': 'Kv17JourneyChange'},
            'advicecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'advicetype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'change': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['openebs.Kv17Change']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_recovered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reasoncontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'reasontype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'subadvicetype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'subreasontype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'openebs.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'company': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['openebs']