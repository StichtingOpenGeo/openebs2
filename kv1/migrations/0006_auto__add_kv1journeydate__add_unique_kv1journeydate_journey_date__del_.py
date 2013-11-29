# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Kv1JourneyDate'
        db.create_table(u'kv1_kv1journeydate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('journey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kv1.Kv1Journey'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'kv1', ['Kv1JourneyDate'])

        # Adding unique constraint on 'Kv1JourneyDate', fields ['journey', 'date']
        db.create_unique(u'kv1_kv1journeydate', ['journey_id', 'date'])

        # Deleting field 'Kv1JourneyStop.scheduledarrival'
        db.delete_column(u'kv1_kv1journeystop', 'scheduledarrival')

        # Deleting field 'Kv1JourneyStop.scheduleddeparture'
        db.delete_column(u'kv1_kv1journeystop', 'scheduleddeparture')

        # Adding field 'Kv1JourneyStop.targetarrival'
        db.add_column(u'kv1_kv1journeystop', 'targetarrival',
                      self.gf('django.db.models.fields.TimeField')(default=datetime.datetime(2013, 11, 29, 0, 0)),
                      keep_default=False)

        # Adding field 'Kv1JourneyStop.targetdeparture'
        db.add_column(u'kv1_kv1journeystop', 'targetdeparture',
                      self.gf('django.db.models.fields.TimeField')(default=datetime.datetime(2013, 11, 29, 0, 0)),
                      keep_default=False)

        # Deleting field 'Kv1Journey.day_monday'
        db.delete_column(u'kv1_kv1journey', 'day_monday')

        # Deleting field 'Kv1Journey.day_wednesday'
        db.delete_column(u'kv1_kv1journey', 'day_wednesday')

        # Deleting field 'Kv1Journey.date_end'
        db.delete_column(u'kv1_kv1journey', 'date_end')

        # Deleting field 'Kv1Journey.day_tuesday'
        db.delete_column(u'kv1_kv1journey', 'day_tuesday')

        # Deleting field 'Kv1Journey.day_saturday'
        db.delete_column(u'kv1_kv1journey', 'day_saturday')

        # Deleting field 'Kv1Journey.day_friday'
        db.delete_column(u'kv1_kv1journey', 'day_friday')

        # Deleting field 'Kv1Journey.day_sunday'
        db.delete_column(u'kv1_kv1journey', 'day_sunday')

        # Deleting field 'Kv1Journey.day_thursday'
        db.delete_column(u'kv1_kv1journey', 'day_thursday')

        # Deleting field 'Kv1Journey.date_start'
        db.delete_column(u'kv1_kv1journey', 'date_start')


    def backwards(self, orm):
        # Removing unique constraint on 'Kv1JourneyDate', fields ['journey', 'date']
        db.delete_unique(u'kv1_kv1journeydate', ['journey_id', 'date'])

        # Deleting model 'Kv1JourneyDate'
        db.delete_table(u'kv1_kv1journeydate')


        # User chose to not deal with backwards NULL issues for 'Kv1JourneyStop.scheduledarrival'
        raise RuntimeError("Cannot reverse this migration. 'Kv1JourneyStop.scheduledarrival' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Kv1JourneyStop.scheduledarrival'
        db.add_column(u'kv1_kv1journeystop', 'scheduledarrival',
                      self.gf('django.db.models.fields.TimeField')(),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Kv1JourneyStop.scheduleddeparture'
        raise RuntimeError("Cannot reverse this migration. 'Kv1JourneyStop.scheduleddeparture' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Kv1JourneyStop.scheduleddeparture'
        db.add_column(u'kv1_kv1journeystop', 'scheduleddeparture',
                      self.gf('django.db.models.fields.TimeField')(),
                      keep_default=False)

        # Deleting field 'Kv1JourneyStop.targetarrival'
        db.delete_column(u'kv1_kv1journeystop', 'targetarrival')

        # Deleting field 'Kv1JourneyStop.targetdeparture'
        db.delete_column(u'kv1_kv1journeystop', 'targetdeparture')

        # Adding field 'Kv1Journey.day_monday'
        db.add_column(u'kv1_kv1journey', 'day_monday',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Kv1Journey.day_wednesday'
        db.add_column(u'kv1_kv1journey', 'day_wednesday',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Kv1Journey.date_end'
        raise RuntimeError("Cannot reverse this migration. 'Kv1Journey.date_end' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Kv1Journey.date_end'
        db.add_column(u'kv1_kv1journey', 'date_end',
                      self.gf('django.db.models.fields.DateField')(),
                      keep_default=False)

        # Adding field 'Kv1Journey.day_tuesday'
        db.add_column(u'kv1_kv1journey', 'day_tuesday',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Kv1Journey.day_saturday'
        db.add_column(u'kv1_kv1journey', 'day_saturday',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Kv1Journey.day_friday'
        db.add_column(u'kv1_kv1journey', 'day_friday',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Kv1Journey.day_sunday'
        db.add_column(u'kv1_kv1journey', 'day_sunday',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Kv1Journey.day_thursday'
        db.add_column(u'kv1_kv1journey', 'day_thursday',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Kv1Journey.date_start'
        raise RuntimeError("Cannot reverse this migration. 'Kv1Journey.date_start' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Kv1Journey.date_start'
        db.add_column(u'kv1_kv1journey', 'date_start',
                      self.gf('django.db.models.fields.DateField')(),
                      keep_default=False)


    models = {
        u'kv1.kv1journey': {
            'Meta': {'unique_together': "(('dataownercode', 'journeynumber'),)", 'object_name': 'Kv1Journey'},
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journeynumber': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '6'}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kv1.Kv1Line']"})
        },
        u'kv1.kv1journeydate': {
            'Meta': {'unique_together': "(('journey', 'date'),)", 'object_name': 'Kv1JourneyDate'},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kv1.Kv1Journey']"})
        },
        u'kv1.kv1journeystop': {
            'Meta': {'unique_together': "(('journey', 'stop'), ('journey', 'stoporder'))", 'object_name': 'Kv1JourneyStop'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kv1.Kv1Journey']"}),
            'stop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kv1.Kv1Stop']"}),
            'stoporder': ('django.db.models.fields.SmallIntegerField', [], {}),
            'stoptype': ('django.db.models.fields.CharField', [], {'default': "'INTERMEDIATE'", 'max_length': '12'}),
            'targetarrival': ('django.db.models.fields.TimeField', [], {}),
            'targetdeparture': ('django.db.models.fields.TimeField', [], {})
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
        }
    }

    complete_apps = ['kv1']