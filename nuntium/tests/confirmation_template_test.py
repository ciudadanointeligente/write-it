from global_test_case import GlobalTestCase as TestCase
from nuntium.models import Confirmation, OutboundMessage
from nuntium.models import Message, WriteItInstance, ConfirmationTemplate
from popit.models import Person
from contactos.models import Contact
from datetime import datetime
from django.core import mail
from plugin_mock.mental_message_plugin import MentalMessage
from subdomains.utils import reverse
from django.contrib.sites.models import Site
from django.utils.unittest import skip
from django.conf import settings
from django.contrib.auth.models import User

class ConfirmationTemplateTestCase(TestCase):
    def setUp(self):
        super(ConfirmationTemplateTestCase,self).setUp()
        self.writeitinstance = WriteItInstance.objects.all()[0]
        self.default_template = ''
        with open('nuntium/templates/nuntium/mails/confirmation/content_template.html', 'r') as f:
           self.default_template = f.read()

        self.default_template_text = ''
        with open('nuntium/templates/nuntium/mails/confirmation/content_template.txt', 'r') as f:
           self.default_template_text = f.read()

        self.default_subject = ''
        with open('nuntium/templates/nuntium/mails/confirmation/subject_template.txt', 'r') as f:
           self.default_subject = f.read()


    def test_instanciate(self):
        confirmation_template = ConfirmationTemplate(writeitinstance=self.writeitinstance)
        self.assertTrue(confirmation_template)
        self.assertEquals(confirmation_template.writeitinstance, self.writeitinstance)
        self.assertEquals(confirmation_template.content_html, self.default_template)
        self.assertEquals(confirmation_template.content_text, self.default_template_text)
        self.assertEquals(confirmation_template.subject, self.default_subject)


