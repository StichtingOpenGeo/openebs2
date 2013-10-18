# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Kv15Scenario'
        db.create_table(u'openebs_kv15scenario', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scenario', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('messagepriority', self.gf('django.db.models.fields.CharField')(default=u'PTPROCESS', max_length=10)),
            ('messagetype', self.gf('django.db.models.fields.CharField')(default=u'GENERAL', max_length=10)),
            ('messagedurationtype', self.gf('django.db.models.fields.CharField')(default=u'ENDTIME', max_length=10)),
            ('messagestarttime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('messageendtime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
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
            ('messagetimestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'openebs', ['Kv15Scenario'])

        # Deleting field 'Kv15Stopmessage.messagescenario'
        db.delete_column(u'openebs_kv15stopmessage', 'messagescenario')


        # Changing field 'Kv15Stopmessage.messagetimestamp'
        db.alter_column(u'openebs_kv15stopmessage', 'messagetimestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))
        # Adding unique constraint on 'Kv15Stopmessage', fields ['dataownercode', 'messagecodedate', 'messagecodenumber']
        db.create_unique(u'openebs_kv15stopmessage', ['dataownercode', 'messagecodedate', 'messagecodenumber'])


    def backwards(self, orm):
        # Removing unique constraint on 'Kv15Stopmessage', fields ['dataownercode', 'messagecodedate', 'messagecodenumber']
        db.delete_unique(u'openebs_kv15stopmessage', ['dataownercode', 'messagecodedate', 'messagecodenumber'])

        # Deleting model 'Kv15Scenario'
        db.delete_table(u'openebs_kv15scenario')

        # Adding field 'Kv15Stopmessage.messagescenario'
        db.add_column(u'openebs_kv15stopmessage', 'messagescenario',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)


        # Changing field 'Kv15Stopmessage.messagetimestamp'
        db.alter_column(u'openebs_kv15stopmessage', 'messagetimestamp', self.gf('django.db.models.fields.DateTimeField')())

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