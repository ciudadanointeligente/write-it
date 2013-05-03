# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MailItTemplate'
        db.create_table(u'mailit_mailittemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject_template', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('content_template', self.gf('django.db.models.fields.TextField')()),
            ('writeitinstance', self.gf('django.db.models.fields.related.OneToOneField')(related_name='mailit_template', unique=True, to=orm['nuntium.WriteItInstance'])),
        ))
        db.send_create_signal(u'mailit', ['MailItTemplate'])


    def backwards(self, orm):
        # Deleting model 'MailItTemplate'
        db.delete_table(u'mailit_mailittemplate')


    models = {
        u'mailit.mailittemplate': {
            'Meta': {'object_name': 'MailItTemplate'},
            'content_template': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject_template': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'writeitinstance': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'mailit_template'", 'unique': 'True', 'to': u"orm['nuntium.WriteItInstance']"})
        },
        u'nuntium.writeitinstance': {
            'Meta': {'object_name': 'WriteItInstance'},
            'api_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['popit.ApiInstance']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'popit.apiinstance': {
            'Meta': {'object_name': 'ApiInstance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('popit.fields.ApiInstanceURLField', [], {'unique': 'True', 'max_length': '200'})
        }
    }

    complete_apps = ['mailit']