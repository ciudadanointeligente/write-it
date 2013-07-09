# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Contact.is_bounced'
        db.add_column(u'contactos_contact', 'is_bounced',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Contact.is_bounced'
        db.delete_column(u'contactos_contact', 'is_bounced')


    models = {
        u'contactos.contact': {
            'Meta': {'object_name': 'Contact'},
            'contact_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contactos.ContactType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_bounced': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['popit.Person']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'contactos.contacttype': {
            'Meta': {'object_name': 'ContactType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
            'image': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'popit_url': ('popit.fields.PopItURLField', [], {'default': "''", 'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['contactos']