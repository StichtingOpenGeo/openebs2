# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Kv15Log'
        db.create_table(u'openebs_kv15log', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('dataownercode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('messagecodedate', self.gf('django.db.models.fields.DateField')()),
            ('messagecodenumber', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=0)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ipaddress', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'openebs', ['Kv15Log'])

        # Adding model 'Kv15Stopmessage'
        db.create_table(u'openebs_kv15stopmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dataownercode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('messagecodedate', self.gf('django.db.models.fields.DateField')()),
            ('messagecodenumber', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=0)),
            ('messagepriority', self.gf('django.db.models.fields.CharField')(default=u'PTPROCESS', max_length=10)),
            ('messagetype', self.gf('django.db.models.fields.CharField')(default=u'GENERAL', max_length=10)),
            ('messagedurationtype', self.gf('django.db.models.fields.CharField')(default=u'ENDTIME', max_length=10)),
            ('messagestarttime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('messageendtime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('messagecontent', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('reasontype', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=0, blank=True)),
            ('subreasontype', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('reasoncontent', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('effecttype', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=0, blank=True)),
            ('subeffecttype', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('effectcontent', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('measuretype', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=0, blank=True)),
            ('submeasuretype', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('measurecontent', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('advicetype', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=0, blank=True)),
            ('subadvicetype', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('advicecontent', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('messagetimestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('messagescenario', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('isdeleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'openebs', ['Kv15Stopmessage'])

        # Adding model 'Kv15Schedule'
        db.create_table(u'openebs_kv15schedule', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('stopmessage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openebs.Kv15Stopmessage'])),
            ('messagestarttime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('messageendtime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('weekdays', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'openebs', ['Kv15Schedule'])

        # Adding model 'Kv15StopmessageUserstopcode'
        db.create_table(u'openebs_kv15stopmessageuserstopcode', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('stopmessage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openebs.Kv15Stopmessage'])),
            ('userstopcode', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'openebs', ['Kv15StopmessageUserstopcode'])

        # Adding model 'Kv15StopmessageLineplanningnumber'
        db.create_table(u'openebs_kv15stopmessagelineplanningnumber', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('stopmessage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openebs.Kv15Stopmessage'])),
            ('lineplanningnumber', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'openebs', ['Kv15StopmessageLineplanningnumber'])


    def backwards(self, orm):
        # Deleting model 'Kv15Log'
        db.delete_table(u'openebs_kv15log')

        # Deleting model 'Kv15Stopmessage'
        db.delete_table(u'openebs_kv15stopmessage')

        # Deleting model 'Kv15Schedule'
        db.delete_table(u'openebs_kv15schedule')

        # Deleting model 'Kv15StopmessageUserstopcode'
        db.delete_table(u'openebs_kv15stopmessageuserstopcode')

        # Deleting model 'Kv15StopmessageLineplanningnumber'
        db.delete_table(u'openebs_kv15stopmessagelineplanningnumber')


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
            'advicetype': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '0', 'blank': 'True'}),
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'effectcontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'effecttype': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '0', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isdeleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'measurecontent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'measuretype': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '0', 'blank': 'True'}),
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
            'reasontype': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '0', 'blank': 'True'}),
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