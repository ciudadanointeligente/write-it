# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from instance.models import PopoloPerson, WriteItInstance
from popolo_sources.models import PopoloSource
from ..models import Confirmation, send_confirmation_email
from ..models import Message, ConfirmationTemplate
from django.core import mail
from subdomains.utils import reverse
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.template import Context, Template
from django.test.utils import override_settings

from contactos.models import Contact, ContactType

import codecs
import os
script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in

from ..user_section.forms import ConfirmationTemplateForm


class ConfirmationTemplateTestCase(TestCase):
    def setUp(self):
        super(ConfirmationTemplateTestCase, self).setUp()
        script_dir = os.path.dirname(__file__)

        self.writeitinstance = WriteItInstance.objects.get(id=1)

        self.default_template_text = ''
        with codecs.open(os.path.join(script_dir, '../templates/nuntium/mails/confirmation/content_template.txt'), 'r', encoding='utf8') as f:
            self.default_template_text = f.read()

        self.default_subject = ''
        with codecs.open(os.path.join(script_dir, '../templates/nuntium/mails/confirmation/subject_template.txt'), 'r', encoding='utf8') as f:
            self.default_subject = f.read()

        self.owner = User.objects.get(id=1)

    def test_instanciate(self):
        """Instanciate the confirmation template"""
        confirmation_template = ConfirmationTemplate(writeitinstance=self.writeitinstance)
        self.assertTrue(confirmation_template)
        self.assertEquals(confirmation_template.writeitinstance, self.writeitinstance)
        self.assertEquals(confirmation_template.content_text, u'')
        self.assertEquals(confirmation_template.subject, u'')

    def test_confirmation_template_with_a_writeitinstance(self):
        """Every time a writeit instance is created then is associated with a confirmation template"""
        writeitinstance = WriteItInstance.objects.create(
            name="New instance",
            slug="new-instance",
            owner=self.owner,
            )

        self.assertTrue(writeitinstance.confirmationtemplate)
        self.assertEquals(writeitinstance.confirmationtemplate.content_html, u'')
        self.assertEquals(writeitinstance.confirmationtemplate.content_text, u'')
        self.assertEquals(writeitinstance.confirmationtemplate.subject, u'')

    def test_confirmation_mail_with_template(self):
        """The confirmation mail is sent using the template"""

        message = Message.objects.get(id=1)
        content_template = "{author_name} {subject}"
        template = message.writeitinstance.confirmationtemplate

        template.content_html = content_template
        template.content_text = content_template
        template.subject = "the subject"
        template.save()

        Confirmation.objects.create(message=message)

        self.assertEquals(len(mail.outbox), 1)  # it is sent to one person pointed in the contact
        self.assertEquals(mail.outbox[0].subject, template.subject)
        self.assertEquals(mail.outbox[0].body, 'Fiera Subject 1')
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertTrue(message.author_email in mail.outbox[0].to)

    def test_confirmation_mail_with_html_template(self):
        """The confirmation mail is sent using the HTML template"""

        message = Message.objects.get(id=1)
        template = message.writeitinstance.confirmationtemplate

        template.content_html = "<b>{subject}<b>"
        template.content_text = "Foo"
        template.subject = "the subject"
        template.save()

        Confirmation.objects.create(message=message)

        self.assertEquals(len(mail.outbox), 1)  # it is sent to one person pointed in the contact
        self.assertEquals(mail.outbox[0].subject, template.subject)
        self.assertEquals(mail.outbox[0].body, "Foo")
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertTrue(message.author_email in mail.outbox[0].to)

        self.assertEquals(
            mail.outbox[0].alternatives,
            [(u'<b>Subject 1<b>', 'text/html')],
            )

    def test_confirmation_mail_without_html_template(self):
        '''The confirmation mail is sent without alternatives or text/html'''
        message = Message.objects.get(id=1)
        template = message.writeitinstance.confirmationtemplate

        template.content_html = ""
        template.content_text = "Foo"
        template.subject = "the subject"
        template.save()

        Confirmation.objects.create(message=message)
        self.assertFalse(mail.outbox[0].alternatives)

    @override_settings(TEMPLATE_STRING_IF_INVALID='!!INVALID!!')
    def test_rendering_templates(self):
        """Render the default confirmation templates and check for errors.

        Set the TEMPLATE_STRING_IF_INVALID setting to something we can find,
        render templates with sensible context, and check that we don't see
        any invalid variable strings.
        """

        owner = User.objects.create(
            username="Test User",
            )
        writeitinstance = WriteItInstance.objects.create(
            name="Test WriteIt Instance",
            owner=owner,
            )
        popolo_source = PopoloSource.objects.get(pk=1)
        recipient = PopoloPerson.objects.create(name='Test Person')
        popolo_source.persons.add(recipient)
        contact_type = ContactType.objects.create(
            name='Contact Type Name',
            label_name='Contact Type Label',
            )
        Contact.objects.create(
            contact_type=contact_type,
            person=recipient,
            value='Test Value',  # What is the value for?
            writeitinstance=writeitinstance,
            )
        message = Message(
            author_name='Message Author',
            author_email='test@example.com',
            subject='Test Message',
            content='Test Content',
            writeitinstance=writeitinstance,
            persons=[recipient],
            )

        # We can't use .create here because we need .save() to
        # create outboundmessage objects.
        message.save()

        # Saving the message with people rather than using create
        # because we need people for the veryfy_people call.
        message.save()

        confirmation = Confirmation.objects.create(
            message=message,
            )

        confirmation_full_url = 'http://example.com/confirmation'
        message_full_url = 'http://example.com/message'

        context = Context(
            {'confirmation': confirmation,
             'confirmation_full_url': confirmation_full_url,
             'message_full_url': message_full_url,
             },
            )

        # Text version
        template = Template(self.default_template_text)
        rendered = template.render(context)
        self.assertNotIn('!!INVALID!!', rendered)


class ConfirmationTemplateFormTestCase(TestCase):
    def setUp(self):
        super(ConfirmationTemplateFormTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.get(id=1)

    def test_instanciate_form(self):
        """Instanciate the form for changing the confirmation template"""
        data = {
            "content_text": "html",
            "subject": "subject",
            }
        form = ConfirmationTemplateForm(data=data,
                                        writeitinstance=self.writeitinstance,
                                        instance=self.writeitinstance.confirmationtemplate)
        self.assertTrue(form.is_valid())
        template = form.save()

        self.assertEquals(template.content_text, data["content_text"])
        self.assertEquals(template.subject, data["subject"])

    def test_instanciate_without_a_writeit_instance_throws_an_error(self):
        """When trying to instanciate the form without a writeit instance it throws an error"""
        data = {
            "content_text": "html",
            "content_html": "text",
            "subject": "subject"
            }
        with self.assertRaises(ValidationError):
            ConfirmationTemplateForm(
                data=data,
                # writeitinstance=self.writeitinstance,
                instance=self.writeitinstance.confirmationtemplate,
                )

    def test_update_url(self):
        """Updating the template using the web"""
        url = reverse('edit_confirmation_template', subdomain=self.writeitinstance.slug)
        self.assertTrue(url)
        c = self.client
        c.login(username="admin", password="admin")
        data = {
            "content_text": "text",
            "subject": "subject",
            }
        response = c.post(url, data=data)
        your_instances_url = reverse(
            'writeitinstance_template_update',
            subdomain=self.writeitinstance.slug,
            )
        self.assertRedirects(response, your_instances_url)
        # it was updated
        template = self.writeitinstance.confirmationtemplate

        self.assertEquals(template.content_text, data["content_text"])
        self.assertEquals(template.subject, data["subject"])


class SendConfirmationEmailTestCase(TestCase):
    def setUp(self):
        owner = User.objects.create(
            username="Test User",
            )
        writeitinstance = WriteItInstance.objects.create(
            name="Test WriteIt Instance",
            owner=owner,
            )
        popolo_source = PopoloSource.objects.get(pk=1)
        recipient = PopoloPerson.objects.create(name='Test Person')
        popolo_source.persons.add(recipient)
        contact_type = ContactType.objects.create(
            name='Contact Type Name',
            label_name='Contact Type Label',
            )
        Contact.objects.create(
            contact_type=contact_type,
            person=recipient,
            value='Test Value',  # What is the value for?
            writeitinstance=writeitinstance,
            )
        message = Message(
            author_name='Message Author',
            author_email='test@example.com',
            subject='Test Message',
            content='Test Content',
            writeitinstance=writeitinstance,
            persons=[recipient],
            )

        # We can't use .create here because we need .save() to
        # create outboundmessage objects.
        message.save()

        # Saving the message with people rather than using create
        # because we need people for the veryfy_people call.
        message.save()

        self.confirmation = Confirmation.objects.create(
            message=message,
            key='fakekey',
            )

        return super(SendConfirmationEmailTestCase, self).setUp()

    @override_settings(SEND_ALL_EMAILS_FROM_DEFAULT_FROM_EMAIL=True,
                       DEFAULT_FROM_EMAIL='from@example.com')
    def test_confirmation_email_public_message(self):
        mail.outbox = []
        send_confirmation_email(None, self.confirmation, True)
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox.pop()

        self.assertEqual(email.subject, u'Please confirm your message to Test Person')
        recipients = email.recipients()
        self.assertEqual(len(recipients), 1)
        self.assertEqual(recipients[0], 'test@example.com')

        expected_body = u"""Hello Message Author


You just submitted a message via Test WriteIt Instance. Please visit
the following link to confirm you want to send this message

http://test-writeit-instance.127.0.0.1.xip.io:8000/en/write/sign/fakekey/

(If you can\u2019t click the link, try copying and pasting it into your
browser\u2019s address bar)

**IMPORTANT** Once confirmed and sent, the message will also be
published on Test WriteIt Instance, where your name, your message, and
any replies, will be public and online for anyone to read, and will
also appear in search engine results.

If this message didn\u2019t come from you (or you\u2019ve changed your mind and
don\u2019t want to send it after all) please just ignore this email.

Thanks for using Test WriteIt Instance, and here is a copy of your
message for your records:


To: Test Person
Subject: Test Message

Test Content"""

        self.assertEqual(email.body, expected_body)
        self.assertEqual(email.content_subtype, u'plain')
        self.assertEqual(email.from_email, u'from@example.com')
