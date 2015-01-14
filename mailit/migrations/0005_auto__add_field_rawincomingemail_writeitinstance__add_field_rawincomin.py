# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'RawIncomingEmail.writeitinstance'
        db.add_column(u'mailit_rawincomingemail', 'writeitinstance',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='raw_emails', null=True, to=orm['nuntium.WriteItInstance']),
                      keep_default=False)

        # Adding field 'RawIncomingEmail.answer'
        db.add_column(u'mailit_rawincomingemail', 'answer',
                      self.gf('django.db.models.fields.related.OneToOneField')(related_name='raw_email', unique=True, null=True, to=orm['nuntium.Answer']),
                      keep_default=False)

        # Adding field 'RawIncomingEmail.problem'
        db.add_column(u'mailit_rawincomingemail', 'problem',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'RawIncomingEmail.writeitinstance'
        db.delete_column(u'mailit_rawincomingemail', 'writeitinstance_id')

        # Deleting field 'RawIncomingEmail.answer'
        db.delete_column(u'mailit_rawincomingemail', 'answer_id')

        # Deleting field 'RawIncomingEmail.problem'
        db.delete_column(u'mailit_rawincomingemail', 'problem')


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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contactos.contact': {
            'Meta': {'object_name': 'Contact'},
            'contact_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contactos.ContactType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_bounced': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contacts'", 'to': u"orm['auth.User']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['popit.Person']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'contactos.contacttype': {
            'Meta': {'object_name': 'ContactType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'mailit.bouncedmessagerecord': {
            'Meta': {'object_name': 'BouncedMessageRecord'},
            'bounce_text': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'outbound_message': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['nuntium.OutboundMessage']", 'unique': 'True'})
        },
        u'mailit.mailittemplate': {
            'Meta': {'object_name': 'MailItTemplate'},
            'content_html_template': ('django.db.models.fields.TextField', [], {'default': "'Hello {{ person }}: <br />\\nYou have a new message: <br />\\n<strong>subject:</strong> {{ subject }} <br />\\n<strong>content:</strong> {{ content }} <br />\\n\\n\\nIf you want to see all the other messages please visit {{ writeit_url }}.<br />\\nSeeya<br />\\n--<br /><br />\\nYou writeIt and we deliverit.'"}),
            'content_template': ('django.db.models.fields.TextField', [], {'default': "'Hello {{ person }}:\\nYou have a new message:\\nsubject: {{ subject }} \\ncontent: {{ content }}\\n\\n\\nIf you want to see all the other messages please visit {{ writeit_url }}.\\nSeeya\\n--\\nYou writeIt and we deliverit.'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject_template': ('django.db.models.fields.CharField', [], {'default': "'[WriteIT] Message: %(subject)s'", 'max_length': '255'}),
            'writeitinstance': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'mailit_template'", 'unique': 'True', 'to': u"orm['nuntium.WriteItInstance']"})
        },
        u'mailit.rawincomingemail': {
            'Meta': {'object_name': 'RawIncomingEmail'},
            'answer': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'raw_email'", 'unique': 'True', 'null': 'True', 'to': u"orm['nuntium.Answer']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'problem': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'writeitinstance': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'raw_emails'", 'null': 'True', 'to': u"orm['nuntium.WriteItInstance']"})
        },
        u'nuntium.answer': {
            'Meta': {'object_name': 'Answer'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': u"orm['nuntium.Message']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['popit.Person']"})
        },
        u'nuntium.membership': {
            'Meta': {'object_name': 'Membership'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['popit.Person']"}),
            'writeitinstance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nuntium.WriteItInstance']"})
        },
        u'nuntium.message': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Message'},
            'author_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'author_name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'confirmated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moderated': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'writeitinstance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nuntium.WriteItInstance']"})
        },
        u'nuntium.outboundmessage': {
            'Meta': {'object_name': 'OutboundMessage'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contactos.Contact']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nuntium.Message']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': "'10'"})
        },
        u'nuntium.writeitinstance': {
            'Meta': {'object_name': 'WriteItInstance'},
            'allow_messages_using_form': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'autoconfirm_api_messages': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moderation_needed_in_all_messages': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'notify_owner_when_new_answer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'writeitinstances'", 'to': u"orm['auth.User']"}),
            'persons': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'writeit_instances'", 'symmetrical': 'False', 'through': u"orm['nuntium.Membership']", 'to': u"orm['popit.Person']"}),
            'rate_limiter': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "'name'", 'unique_with': '()'})
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
            'popit_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'popit_url': ('popit.fields.PopItURLField', [], {'default': "''", 'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['mailit']