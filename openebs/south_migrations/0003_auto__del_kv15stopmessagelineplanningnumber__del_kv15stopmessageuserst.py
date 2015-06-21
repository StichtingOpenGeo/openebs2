# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Kv15StopmessageLineplanningnumber'
        db.delete_table(u'openebs_kv15stopmessagelineplanningnumber')

        # Deleting model 'Kv15StopmessageUserstopcode'
        db.delete_table(u'openebs_kv15stopmessageuserstopcode')

        # Adding model 'Kv15MessageLine'
        db.create_table(u'openebs_kv15messageline', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('stopmessage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openebs.Kv15Stopmessage'])),
            ('line', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kv1.Kv1Line'])),
        ))
        db.send_create_signal(u'openebs', ['Kv15MessageLine'])

        # Adding model 'Kv15ScenarioStop'
        db.create_table(u'openebs_kv15scenariostop', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openebs.Kv15ScenarioMessage'])),
            ('stop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kv1.Kv1Stop'])),
        ))
        db.send_create_signal(u'openebs', ['Kv15ScenarioStop'])

        # Adding model 'Kv15ScenarioMessage'
        db.create_table(u'openebs_kv15scenariomessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scenario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openebs.Kv15Scenario'])),
            ('messagepriority', self.gf('django.db.models.fields.CharField')(default=u'PTPROCESS', max_length=10)),
            ('messagetype', self.gf('django.db.models.fields.CharField')(default=u'GENERAL', max_length=10)),
            ('messagedurationtype', self.gf('django.db.models.fields.CharField')(default=u'ENDTIME', max_length=10)),
            ('messagecontent', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('reasontype', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('subreasontype', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('reasoncontent', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('effecttype', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('subeffecttype', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('effectcontent', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('measuretype', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('submeasuretype', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('measurecontent', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('advicetype', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('subadvicetype', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('advicecontent', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'openebs', ['Kv15ScenarioMessage'])

        # Adding model 'Kv15MessageStop'
        db.create_table(u'openebs_kv15messagestop', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('stopmessage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openebs.Kv15Stopmessage'])),
            ('stop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kv1.Kv1Stop'])),
        ))
        db.send_create_signal(u'openebs', ['Kv15MessageStop'])

        # Deleting field 'Kv15Scenario.effecttype'
        db.delete_column(u'openebs_kv15scenario', 'effecttype')

        # Deleting field 'Kv15Scenario.messagedurationtype'
        db.delete_column(u'openebs_kv15scenario', 'messagedurationtype')

        # Deleting field 'Kv15Scenario.subeffecttype'
        db.delete_column(u'openebs_kv15scenario', 'subeffecttype')

        # Deleting field 'Kv15Scenario.reasontype'
        db.delete_column(u'openebs_kv15scenario', 'reasontype')

        # Deleting field 'Kv15Scenario.messageendtime'
        db.delete_column(u'openebs_kv15scenario', 'messageendtime')

        # Deleting field 'Kv15Scenario.subreasontype'
        db.delete_column(u'openebs_kv15scenario', 'subreasontype')

        # Deleting field 'Kv15Scenario.measuretype'
        db.delete_column(u'openebs_kv15scenario', 'measuretype')

        # Deleting field 'Kv15Scenario.messagetimestamp'
        db.delete_column(u'openebs_kv15scenario', 'messagetimestamp')

        # Deleting field 'Kv15Scenario.messagetype'
        db.delete_column(u'openebs_kv15scenario', 'messagetype')

        # Deleting field 'Kv15Scenario.submeasuretype'
        db.delete_column(u'openebs_kv15scenario', 'submeasuretype')

        # Deleting field 'Kv15Scenario.effectcontent'
        db.delete_column(u'openebs_kv15scenario', 'effectcontent')

        # Deleting field 'Kv15Scenario.reasoncontent'
        db.delete_column(u'openebs_kv15scenario', 'reasoncontent')

        # Deleting field 'Kv15Scenario.subadvicetype'
        db.delete_column(u'openebs_kv15scenario', 'subadvicetype')

        # Deleting field 'Kv15Scenario.scenario'
        db.delete_column(u'openebs_kv15scenario', 'scenario')

        # Deleting field 'Kv15Scenario.measurecontent'
        db.delete_column(u'openebs_kv15scenario', 'measurecontent')

        # Deleting field 'Kv15Scenario.messagepriority'
        db.delete_column(u'openebs_kv15scenario', 'messagepriority')

        # Deleting field 'Kv15Scenario.advicetype'
        db.delete_column(u'openebs_kv15scenario', 'advicetype')

        # Deleting field 'Kv15Scenario.messagestarttime'
        db.delete_column(u'openebs_kv15scenario', 'messagestarttime')

        # Deleting field 'Kv15Scenario.advicecontent'
        db.delete_column(u'openebs_kv15scenario', 'advicecontent')

        # Deleting field 'Kv15Scenario.messagecontent'
        db.delete_column(u'openebs_kv15scenario', 'messagecontent')

        # Adding field 'Kv15Scenario.name'
        db.add_column(u'openebs_kv15scenario', 'name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'Kv15Scenario.description'
        db.add_column(u'openebs_kv15scenario', 'description',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'Kv15StopmessageLineplanningnumber'
        db.create_table(u'openebs_kv15stopmessagelineplanningnumber', (
            ('line', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kv1.Kv1Line'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('stopmessage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openebs.Kv15Stopmessage'])),
        ))
        db.send_create_signal(u'openebs', ['Kv15StopmessageLineplanningnumber'])

        # Adding model 'Kv15StopmessageUserstopcode'
        db.create_table(u'openebs_kv15stopmessageuserstopcode', (
            ('stop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kv1.Kv1Stop'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('stopmessage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openebs.Kv15Stopmessage'])),
        ))
        db.send_create_signal(u'openebs', ['Kv15StopmessageUserstopcode'])

        # Deleting model 'Kv15MessageLine'
        db.delete_table(u'openebs_kv15messageline')

        # Deleting model 'Kv15ScenarioStop'
        db.delete_table(u'openebs_kv15scenariostop')

        # Deleting model 'Kv15ScenarioMessage'
        db.delete_table(u'openebs_kv15scenariomessage')

        # Deleting model 'Kv15MessageStop'
        db.delete_table(u'openebs_kv15messagestop')

        # Adding field 'Kv15Scenario.effecttype'
        db.add_column(u'openebs_kv15scenario', 'effecttype',
                      self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Kv15Scenario.messagedurationtype'
        db.add_column(u'openebs_kv15scenario', 'messagedurationtype',
                      self.gf('django.db.models.fields.CharField')(default=u'ENDTIME', max_length=10),
                      keep_default=False)

        # Adding field 'Kv15Scenario.subeffecttype'
        db.add_column(u'openebs_kv15scenario', 'subeffecttype',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True),
                      keep_default=False)

        # Adding field 'Kv15Scenario.reasontype'
        db.add_column(u'openebs_kv15scenario', 'reasontype',
                      self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Kv15Scenario.messageendtime'
        db.add_column(u'openebs_kv15scenario', 'messageendtime',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Kv15Scenario.subreasontype'
        db.add_column(u'openebs_kv15scenario', 'subreasontype',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True),
                      keep_default=False)

        # Adding field 'Kv15Scenario.measuretype'
        db.add_column(u'openebs_kv15scenario', 'measuretype',
                      self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Kv15Scenario.messagetimestamp'
        raise RuntimeError("Cannot reverse this migration. 'Kv15Scenario.messagetimestamp' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Kv15Scenario.messagetimestamp'
        db.add_column(u'openebs_kv15scenario', 'messagetimestamp',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True),
                      keep_default=False)

        # Adding field 'Kv15Scenario.messagetype'
        db.add_column(u'openebs_kv15scenario', 'messagetype',
                      self.gf('django.db.models.fields.CharField')(default=u'GENERAL', max_length=10),
                      keep_default=False)

        # Adding field 'Kv15Scenario.submeasuretype'
        db.add_column(u'openebs_kv15scenario', 'submeasuretype',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True),
                      keep_default=False)

        # Adding field 'Kv15Scenario.effectcontent'
        db.add_column(u'openebs_kv15scenario', 'effectcontent',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Kv15Scenario.reasoncontent'
        db.add_column(u'openebs_kv15scenario', 'reasoncontent',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Kv15Scenario.subadvicetype'
        db.add_column(u'openebs_kv15scenario', 'subadvicetype',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True),
                      keep_default=False)

        # Adding field 'Kv15Scenario.scenario'
        db.add_column(u'openebs_kv15scenario', 'scenario',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Kv15Scenario.measurecontent'
        db.add_column(u'openebs_kv15scenario', 'measurecontent',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Kv15Scenario.messagepriority'
        db.add_column(u'openebs_kv15scenario', 'messagepriority',
                      self.gf('django.db.models.fields.CharField')(default=u'PTPROCESS', max_length=10),
                      keep_default=False)

        # Adding field 'Kv15Scenario.advicetype'
        db.add_column(u'openebs_kv15scenario', 'advicetype',
                      self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Kv15Scenario.messagestarttime'
        db.add_column(u'openebs_kv15scenario', 'messagestarttime',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Kv15Scenario.advicecontent'
        db.add_column(u'openebs_kv15scenario', 'advicecontent',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Kv15Scenario.messagecontent'
        db.add_column(u'openebs_kv15scenario', 'messagecontent',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Deleting field 'Kv15Scenario.name'
        db.delete_column(u'openebs_kv15scenario', 'name')

        # Deleting field 'Kv15Scenario.description'
        db.delete_column(u'openebs_kv15scenario', 'description')


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
            'Meta': {'object_name': 'Kv15MessageLine'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kv1.Kv1Line']"}),
            'stopmessage': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['openebs.Kv15Stopmessage']"})
        },
        u'openebs.kv15messagestop': {
            'Meta': {'object_name': 'Kv15MessageStop'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kv1.Kv1Stop']"}),
            'stopmessage': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['openebs.Kv15Stopmessage']"})
        },
        u'openebs.kv15scenario': {
            'Meta': {'object_name': 'Kv15Scenario'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'openebs.kv15scenariomessage': {
            'Meta': {'object_name': 'Kv15ScenarioMessage'},
            'advicecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'advicetype': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
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
        u'openebs.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'company': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['openebs']