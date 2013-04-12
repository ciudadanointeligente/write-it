# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ContactType'
        db.create_table(u'contactos_contacttype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('label_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'contactos', ['ContactType'])

        # Adding model 'Contact'
        db.create_table(u'contactos_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contact_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contactos.ContactType'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['popit.Person'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=512)),
        ))
        db.send_create_signal(u'contactos', ['Contact'])


    def backwards(self, orm):
        # Deleting model 'ContactType'
        db.delete_table(u'contactos_contacttype')

        # Deleting model 'Contact'
        db.delete_table(u'contactos_contact')


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

    complete_apps = ['contactos']