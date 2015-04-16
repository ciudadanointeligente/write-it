# -*- coding: utf-8 -*-
import re

from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models


old_new_answer_text = u'''Dear {author_name}

{person} has replied to your {writeit_name}
message with subject

"{subject}"


You can see their response at

{message_url}


{person} said:

{content}

-- 

Thanks for using {writeit_name}
'''

old_new_answer_subject = u'{person} has replied to your message {subject}'

old_confirmation_text = u'''Hello {author_name}


You just submitted a message via {writeit_name}. Please visit the following link to confirm you want to send this message

{confirmation_url}

(If you can’t click the link, try copying and pasting it into your browser’s address bar)

**IMPORTANT** Once confirmed and sent, the message will also be published on {writeit_name}, where your name, your message, and any replies, will be public and online for anyone to read, and will also appear in search engine results.

If this message didn’t come from you (or you’ve changed your mind and don’t want to send it after all) please just ignore this email.

Thanks for using {writeit_name}, and here is a copy of your message for your records:


To: {recipients}
Subject: {subject}

{content}
'''

old_confirmation_subject = u'''Please confirm your WriteIt message to {recipients}'''


def whitespace_ignoring_equal(a, b):
    def squash(x):
        return re.sub('\s', '', x)

    return squash(a) == squash(b)


class Migration(DataMigration):
    def forwards(self, orm):
        for instance in orm.WriteItInstance.objects.all():
            confirmation_template = instance.confirmationtemplate

            if whitespace_ignoring_equal(confirmation_template.content_text, old_confirmation_text):
                confirmation_template.content_text = u''
                confirmation_template.save()

            if whitespace_ignoring_equal(confirmation_template.subject, old_confirmation_subject):
                confirmation_template.subject = u''
                confirmation_template.save()

            new_answer_template = instance.new_answer_notification_template

            if whitespace_ignoring_equal(new_answer_template.template_text, old_new_answer_text):
                new_answer_template.template_text = u''
                new_answer_template.save()

            if whitespace_ignoring_equal(new_answer_template.subject_template, old_new_answer_subject):
                new_answer_template.subject_template = u''
                new_answer_template.save()


    def backwards(self, orm):
        for instance in orm.WriteItInstance.objects.all():
            confirmation_template = instance.confirmationtemplate

            if whitespace_ignoring_equal(confirmation_template.content_text, u''):
                confirmation_template.content_text = old_confirmation_text
                confirmation_template.save()

            if whitespace_ignoring_equal(confirmation_template.subject, u''):
                confirmation_template.subject = old_confirmation_subject
                confirmation_template.save()

            new_answer_template = instance.new_answer_notification_template

            if whitespace_ignoring_equal(new_answer_template.template_text, u''):
                new_answer_template.template_text = old_new_answer_text
                new_answer_template.save()

            if whitespace_ignoring_equal(new_answer_template.subject_template, u''):
                new_answer_template.subject_template = old_new_answer_subject
                new_answer_template.save()


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
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
            'content_html': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': u"orm['nuntium.Message']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['popit.Person']"})
        },
        u'nuntium.answerattachment': {
            'Meta': {'object_name': 'AnswerAttachment'},
            'answer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': u"orm['nuntium.Answer']"}),
            'content': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '512'})
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
            'created': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2015, 4, 15, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'message': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['nuntium.Message']", 'unique': 'True'})
        },
        u'nuntium.confirmationtemplate': {
            'Meta': {'object_name': 'ConfirmationTemplate'},
            'content_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content_text': ('django.db.models.fields.TextField', [], {'default': "u'Hello {author_name}\\n\\n\\nYou just submitted a message via {writeit_name}. Please visit the following link to confirm you want to send this message\\n\\n{confirmation_url}\\n\\n(If you can\\u2019t click the link, try copying and pasting it into your browser\\u2019s address bar)\\n\\n**IMPORTANT** Once confirmed and sent, the message will also be published on {writeit_name}, where your name, your message, and any replies, will be public and online for anyone to read, and will also appear in search engine results.\\n\\nIf this message didn\\u2019t come from you (or you\\u2019ve changed your mind and don\\u2019t want to send it after all) please just ignore this email.\\n\\nThanks for using {writeit_name}, and here is a copy of your message for your records:\\n\\n\\nTo: {recipients}\\nSubject: {subject}\\n\\n{content}\\n'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'default': "u'Please confirm your WriteIt message to {recipients}\\n'", 'max_length': '512'}),
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
            'datetime': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2015, 4, 15, 0, 0)'}),
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
            'subject_template': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'template_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'template_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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
            'description': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
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
            'can_create_answer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'custom_from_domain': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'email_host': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'email_host_password': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'email_host_user': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'email_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'email_use_ssl': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'email_use_tls': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_recipients': ('django.db.models.fields.PositiveIntegerField', [], {'default': '5'}),
            'moderation_needed_in_all_messages': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notify_owner_when_new_answer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rate_limiter': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'testing_mode': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'writeitinstance': ('annoying.fields.AutoOneToOneField', [], {'related_name': "'config'", 'unique': 'True', 'to': u"orm['nuntium.WriteItInstance']"})
        },
        u'nuntium.writeitinstancepopitinstancerecord': {
            'Meta': {'object_name': 'WriteitInstancePopitInstanceRecord'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'periodicity': ('django.db.models.fields.CharField', [], {'default': "'1W'", 'max_length': "'2'"}),
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
    symmetrical = True
