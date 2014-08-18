from global_test_case import GlobalTestCase as TestCase
from ..models import Confirmation, OutboundMessage
from ..models import Message, WriteItInstance, ConfirmationTemplate
from popit.models import Person
from contactos.models import Contact
from datetime import datetime
from django.core import mail
from plugin_mock.mental_message_plugin import MentalMessage
from django.core.urlresolvers  import reverse
from django.contrib.sites.models import Site
from django.utils.unittest import skip
from django.conf import settings
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.template import Context, Template
from django.test.client import Client
import os
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in

class ConfirmationTemplateTestCase(TestCase):
    def setUp(self):
        super(ConfirmationTemplateTestCase,self).setUp()
        script_dir = os.path.dirname(__file__)

        self.writeitinstance = WriteItInstance.objects.all()[0]
        self.default_template = ''
        with open(os.path.join(script_dir, '../templates/nuntium/mails/confirmation/content_template.html'), 'r') as f:
           self.default_template = f.read()

        self.default_template_text = ''
        with open(os.path.join(script_dir, '../templates/nuntium/mails/confirmation/content_template.txt'), 'r') as f:
           self.default_template_text = f.read()

        self.default_subject = ''
        with open(os.path.join(script_dir, '../templates/nuntium/mails/confirmation/subject_template.txt'), 'r') as f:
           self.default_subject = f.read()

        self.owner = User.objects.all()[0]


    def test_instanciate(self):
        """Instanciate the confirmation template"""
        confirmation_template = ConfirmationTemplate(writeitinstance=self.writeitinstance)
        self.assertTrue(confirmation_template)
        self.assertEquals(confirmation_template.writeitinstance, self.writeitinstance)
        self.assertEquals(confirmation_template.content_html, self.default_template)
        self.assertEquals(confirmation_template.content_text, self.default_template_text)
        self.assertEquals(confirmation_template.subject, self.default_subject)

    def test_confirmation_template_with_a_writeitinstance(self):
        """Every time a writeit instance is created then is associated with a confirmation template"""
        writeitinstance = WriteItInstance.objects.create(name="New instance",\
                                                         slug="new-instance",\
                                                         owner=self.owner)

        self.assertTrue(writeitinstance.confirmationtemplate)
        self.assertEquals(writeitinstance.confirmationtemplate.content_html, self.default_template)
        self.assertEquals(writeitinstance.confirmationtemplate.content_text, self.default_template_text)
        self.assertEquals(writeitinstance.confirmationtemplate.subject, self.default_subject)


    def test_confirmation_mail_with_template(self):
        """The confirmation mail is sent using the template"""

        message = Message.objects.all()[0]
        content_template = "{{confirmation}}{{confirmation_full_url}}{{message_full_url}}"
        template = message.writeitinstance.confirmationtemplate

        template.content_html = content_template
        template.content_text = content_template
        template.subject = "the subject"
        template.save()

        confirmation = Confirmation.objects.create(message=message)
        # Then I create a confirmation a mail is sent
        url = reverse('confirm', kwargs={
            'slug':confirmation.key
            })
        current_site = Site.objects.get_current()
        confirmation_full_url = url

        message_full_url = message.get_absolute_url()
        content_template_template = Template(content_template)
        context = Context({'confirmation':confirmation,
                                                 'confirmation_full_url':confirmation_full_url,
                                                 'message_full_url':message_full_url
            })
        expected_body = content_template_template.render(context)

        self.assertEquals(len(mail.outbox), 1) #it is sent to one person pointed in the contact
        self.assertEquals(mail.outbox[0].subject, template.subject)
        self.assertEquals(mail.outbox[0].body, expected_body)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertTrue(message.author_email in mail.outbox[0].to)

from ..user_section.forms import ConfirmationTemplateForm

class ConfirmationTemplateFormTestCase(TestCase):
    def setUp(self):
        super(ConfirmationTemplateFormTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.all()[0]


    def test_instanciate_form(self):
        """Instanciate the form for changing the confirmation template"""
        data = {
            "content_text":"html",
            "content_html":"text",
            "subject" : "subject"
        }
        form = ConfirmationTemplateForm(data=data,
                                        writeitinstance=self.writeitinstance,
                                        instance=self.writeitinstance.confirmationtemplate)
        self.assertTrue(form.is_valid())
        template = form.save()

        self.assertEquals(template.content_text, data["content_text"])
        self.assertEquals(template.content_html, data["content_html"])
        self.assertEquals(template.subject, data["subject"])

    def test_instanciate_without_a_writeit_instance_throws_an_error(self):
        """When trying to instanciate the form without a writeit instance it throws an error"""
        data = {
            "content_text":"html",
            "content_html":"text",
            "subject" : "subject"
        }
        with self.assertRaises(ValidationError) as error:
            form = ConfirmationTemplateForm(data=data,
                                            #writeitinstance=self.writeitinstance,
                                            instance=self.writeitinstance.confirmationtemplate)

    def test_update_url(self):
        """Updating the template using the web"""
        url = reverse('edit_confirmation_template', kwargs={'pk':self.writeitinstance.pk})
        self.assertTrue(url)
        c = Client()
        c.login(username="admin", password="admin")
        data = {
            "content_text":"html",
            "content_html":"text",
            "subject" : "subject"
        }
        response = c.post(url, data=data)
        your_instances_url = reverse('writeitinstance_template_update',\
            kwargs={"pk":self.writeitinstance.id})
        self.assertRedirects(response, your_instances_url)
        #it was updated
        template = self.writeitinstance.confirmationtemplate

        self.assertEquals(template.content_html, data["content_html"])
        self.assertEquals(template.content_text, data["content_text"])
        self.assertEquals(template.subject, data["subject"])



