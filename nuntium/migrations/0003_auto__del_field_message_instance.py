# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Message.instance'
        db.delete_column(u'nuntium_message', 'instance_id')


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Message.instance'
        raise RuntimeError("Cannot reverse this migration. 'Message.instance' and its values cannot be restored.")

    models = {
        u'contactos.contact': {
            'Meta': {'object_name': 'Contact'},
            'contact_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contactos.ContactType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['popit.Person']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'contactos.contacttype': {
            'Meta': {'object_name': 'ContactType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'nuntium.instance': {
            'Meta': {'object_name': 'Instance'},
            'api_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['popit.ApiInstance']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'nuntium.message': {
            'Meta': {'object_name': 'Message'},
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'nuntium.outboundmessage': {
            'Meta': {'object_name': 'OutboundMessage'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contactos.Contact']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nuntium.Message']"})
        },
        u'popit.apiinstance': {
            'Meta': {'object_name': 'ApiInstance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('popit.fields.ApiInstanceURLField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'popit.person': {
            'Meta': {'object_name': 'Person'},
            'api_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['popit.ApiInstance']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'popit_url': ('popit.fields.PopItURLField', [], {'default': "''", 'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['nuntium']