from global_test_case import GlobalTestCase as TestCase
from django.utils.unittest import skip
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.translation import ugettext as _
from contactos.models import Contact, ContactType
from nuntium.models import Message, WriteItInstance, OutboundMessage, MessageRecord
from popit.models import Person, ApiInstance
from django.contrib.contenttypes.models import ContentType


class TestMessages(TestCase):

    def setUp(self):
        super(TestMessages,self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.person1 = Person.objects.all()[0]


    def test_create_message(self):
        message = Message.objects.create(content = 'Content 1', author_name='Felipe', author_email="falvarez@votainteligente.cl", subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])
        self.assertTrue(message)
        self.assertEquals(message.content, "Content 1")
        self.assertEquals(message.subject, "Subject 1")
        self.assertEquals(message.writeitinstance, self.writeitinstance1)

    def test_message_unicode(self):
        message = Message.objects.create(content = 'Content 1', author_name='Felipe', author_email="falvarez@votainteligente.cl", subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])

        self.assertEquals(message.__unicode__(), _('%(subject)s at %(instance)s') % {
            'subject':message.subject,
            'instance':self.writeitinstance1.name
            })

    def test_outboundmessage_create_without_manager(self):
        message = Message(content = 'Content 1', author_name='Felipe', author_email="falvarez@votainteligente.cl", subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])
        message.save()

        
        self.assertEquals(message.outboundmessage_set.count(), 1)


    def test_it_creates_outbound_messages_only_once(self):
        message = Message.objects.create(content = 'Content 1', author_name='Felipe', author_email="falvarez@votainteligente.cl", subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])
        message.save()

        self.assertEquals(OutboundMessage.objects.filter(message=message).count(), 1)

    def test_it_raises_typeerror_when_no_contacts_are_present(self):
        with self.assertRaises(TypeError):
            Message.objects.create(content = 'Content 1', author_name='Felipe', author_email="falvarez@votainteligente.cl", subject='Subject 1', writeitinstance= self.writeitinstance1)
    




