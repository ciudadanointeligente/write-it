# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'WriteItInstance.allow_messages_using_form'
        db.delete_column(u'nuntium_writeitinstance', 'allow_messages_using_form')

        # Deleting field 'WriteItInstance.notify_owner_when_new_answer'
        db.delete_column(u'nuntium_writeitinstance', 'notify_owner_when_new_answer')

        # Deleting field 'WriteItInstance.autoconfirm_api_messages'
        db.delete_column(u'nuntium_writeitinstance', 'autoconfirm_api_messages')

        # Deleting field 'WriteItInstance.moderation_needed_in_all_messages'
        db.delete_column(u'nuntium_writeitinstance', 'moderation_needed_in_all_messages')

        # Deleting field 'WriteItInstance.rate_limiter'
        db.delete_column(u'nuntium_writeitinstance', 'rate_limiter')


    def backwards(self, orm):
        # Adding field 'WriteItInstance.allow_messages_using_form'
        db.add_column(u'nuntium_writeitinstance', 'allow_messages_using_form',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'WriteItInstance.notify_owner_when_new_answer'
        db.add_column(u'nuntium_writeitinstance', 'notify_owner_when_new_answer',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'WriteItInstance.autoconfirm_api_messages'
        db.add_column(u'nuntium_writeitinstance', 'autoconfirm_api_messages',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'WriteItInstance.moderation_needed_in_all_messages'
        db.add_column(u'nuntium_writeitinstance', 'moderation_needed_in_all_messages',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'WriteItInstance.rate_limiter'
        db.add_column(u'nuntium_writeitinstance', 'rate_limiter',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


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
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contacts'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['popit.Person']"}),
            'popit_identifier': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'writeitinstance': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contacts'", 'null': 'True', 'to': u"orm['nuntium.WriteItInstance']"})
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
        u'djangoplugins.plugin': {
            'Meta': {'ordering': "(u'_order',)", 'unique_together': "(('point', 'name'),)", 'object_name': 'Plugin'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'point': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['djangoplugins.PluginPoint']"}),
            'pythonpath': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        u'djangoplugins.pluginpoint': {
            'Meta': {'object_name': 'PluginPoint'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pythonpath': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'nuntium.answer': {
            'Meta': {'object_name': 'Answer'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': u"orm['nuntium.Message']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['popit.Person']"})
        },
        u'nuntium.answerwebhook': {
            'Meta': {'object_name': 'AnswerWebHook'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            'writeitinstance': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answer_webhooks'", 'to': u"orm['nuntium.WriteItInstance']"})
        },
        u'nuntium.confirmation': {
            'Meta': {'object_name': 'Confirmation'},
            'confirmated_at': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True'}),
            'created': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2015, 2, 12, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'message': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['nuntium.Message']", 'unique': 'True'})
        },
        u'nuntium.confirmationtemplate': {
            'Meta': {'object_name': 'ConfirmationTemplate'},
            'content_html': ('django.db.models.fields.TextField', [], {'default': '\'Hello {{ confirmation.message.author_name }}:<br />\\nWe have received a message written by you in {{ site.current_site.domain }}.<br />\\nThe message was:<br />\\n<strong>Subject: </strong> {{ confirmation.message.subject }} <br/>\\n<strong>Content: </strong> {{ confirmation.message.content|linebreaks }} <br />\\n<strong>To: </strong>\\n<ul>\\n\\t{% for person in confirmation.message.people %}\\n\\t<li>{{ person.name }}</li>\\n\\t{% endfor %}\\n</ul>\\n<br />\\n\\nPlease confirm that you have sent this message by clicking on the next link<br />\\n<br />\\n<a href="{{ confirmation_full_url }}">{{ confirmation_full_url }}</a>.\\n<br />\\n{% if confirmation.message.public %}\\n<br />\\nOnce you have confirmed, you will be able to access your message if you go to the next url<br />\\n<br />\\n<a href="{{ message_full_url }}">{{ message_full_url }}</a>.\\n{% endif %}\\n<br />\\n\\nThanks\\n\\nThe writeit team.\''}),
            'content_text': ('django.db.models.fields.TextField', [], {'default': "'Hello {{ confirmation.message.author_name }}:\\nWe have received a message written by you in {{ site.current_site.domain }}.\\nThe message was:\\nSubject:  {{ confirmation.message.subject }} \\nContent:  {{ confirmation.message.content|linebreaks }}\\nTo: {% for person in confirmation.message.people %}\\n{{ person.name }}\\n{% endfor %}\\n\\nPlease confirm that you have sent this message by copiying the next url in your browser.\\n\\n\\n{{ confirmation_full_url }}.\\n{% if confirmation.message.public %}\\n\\nOnce you have confirmed, you will be able to access your message if you go to the next url\\n\\n\\n{{ message_full_url }}.\\n\\n{% endif %}\\n\\nThanks.\\n\\nThe writeit team.'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'default': "'Confirmation email for a message in WriteIt\\n'", 'max_length': '512'}),
            'writeitinstance': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['nuntium.WriteItInstance']", 'unique': 'True'})
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
        u'nuntium.messagerecord': {
            'Meta': {'object_name': 'MessageRecord'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'datetime': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2015, 2, 12, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'nuntium.moderation': {
            'Meta': {'object_name': 'Moderation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'message': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'moderation'", 'unique': 'True', 'to': u"orm['nuntium.Message']"})
        },
        u'nuntium.newanswernotificationtemplate': {
            'Meta': {'object_name': 'NewAnswerNotificationTemplate'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject_template': ('django.db.models.fields.CharField', [], {'default': "'%(person)s has answered to your message %(message)s'", 'max_length': '255'}),
            'template_html': ('django.db.models.fields.TextField', [], {'default': '\'Dear {{user}}: <br/>\\n<br/>\\nWe received an answer from {{person}} to your message "{{message.subject}}" and the answer is:<br/>\\n<br/>\\n{{answer.content}}<br/>\\n<br/>\\nThanks for using Write-It<br/>\\n-- <br/>\\nThe Write-it Team\''}),
            'template_text': ('django.db.models.fields.TextField', [], {'default': '\'Dear {{user}}:\\n\\nWe received an answer from {{person}} to your message "{{message.subject}}" and the answer is:\\n\\n{{answer.content}}\\n\\nThanks for using Write-It\\n-- \\nThe Write-it Team\''}),
            'writeitinstance': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'new_answer_notification_template'", 'unique': 'True', 'to': u"orm['nuntium.WriteItInstance']"})
        },
        u'nuntium.nocontactom': {
            'Meta': {'object_name': 'NoContactOM'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nuntium.Message']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['popit.Person']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': "'10'"})
        },
        u'nuntium.outboundmessage': {
            'Meta': {'object_name': 'OutboundMessage'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contactos.Contact']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nuntium.Message']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': "'10'"})
        },
        u'nuntium.outboundmessageidentifier': {
            'Meta': {'object_name': 'OutboundMessageIdentifier'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'outbound_message': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['nuntium.OutboundMessage']", 'unique': 'True'})
        },
        u'nuntium.outboundmessagepluginrecord': {
            'Meta': {'object_name': 'OutboundMessagePluginRecord'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number_of_attempts': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'outbound_message': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nuntium.OutboundMessage']"}),
            'plugin': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['djangoplugins.Plugin']"}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'try_again': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'nuntium.ratelimiter': {
            'Meta': {'object_name': 'RateLimiter'},
            'count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'day': ('django.db.models.fields.DateField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'writeitinstance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nuntium.WriteItInstance']"})
        },
        u'nuntium.subscriber': {
            'Meta': {'object_name': 'Subscriber'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subscribers'", 'to': u"orm['nuntium.Message']"})
        },
        u'nuntium.writeitinstance': {
            'Meta': {'object_name': 'WriteItInstance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'writeitinstances'", 'to': u"orm['auth.User']"}),
            'persons': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'writeit_instances'", 'symmetrical': 'False', 'through': u"orm['nuntium.Membership']", 'to': u"orm['popit.Person']"}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "'name'", 'unique_with': '()'})
        },
        u'nuntium.writeitinstanceconfig': {
            'Meta': {'object_name': 'WriteItInstanceConfig'},
            'allow_messages_using_form': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'autoconfirm_api_messages': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moderation_needed_in_all_messages': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notify_owner_when_new_answer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rate_limiter': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'testing_mode': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'writeitinstance': ('annoying.fields.AutoOneToOneField', [], {'related_name': "'config'", 'unique': 'True', 'to': u"orm['nuntium.WriteItInstance']"})
        },
        u'nuntium.writeitinstancepopitinstancerecord': {
            'Meta': {'object_name': 'WriteitInstancePopitInstanceRecord'},
            'autosync': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'popitapiinstance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['popit.ApiInstance']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'nothing'", 'max_length': "'20'"}),
            'status_explanation': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'writeitinstance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nuntium.WriteItInstance']"})
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

    complete_apps = ['nuntium']