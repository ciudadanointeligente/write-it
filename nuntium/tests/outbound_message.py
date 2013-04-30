from global_test_case import GlobalTestCase as TestCase
from django.utils.unittest import skip
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.translation import ugettext as _
from contactos.models import Contact, ContactType
from nuntium.models import Message, WriteItInstance, OutboundMessage, MessageRecord
from popit.models import Person, ApiInstance
from django.contrib.contenttypes.models import ContentType

class OutboundMessageTestCase(TestCase):
    def setUp(self):
        super(OutboundMessageTestCase,self).setUp()
        self.api_instance1 = ApiInstance.objects.all()[0]
        self.contact1 = Contact.objects.all()[0]
        self.message = Message.objects.all()[0]


    def test_create_a_outbound_message(self):
        outbound_message = OutboundMessage.objects.create(message = self.message, contact=self.contact1)
        #This means that there is a link between a contact and a message
        self.assertTrue(outbound_message)
        self.assertEquals(outbound_message.status, "ready")


    def test_outbound_message_unicode(self):
        outbound_message = OutboundMessage.objects.create(message = self.message, contact=self.contact1)
        expected_unicode = _('%(subject)s sent to %(person)s (%(contact)s) at %(instance)s') % {
            'subject': self.message.subject,
            'person':self.contact1.person.name,
            'contact':self.contact1.value,
            'instance':self.message.writeitinstance.name
        }
        self.assertEquals(outbound_message.__unicode__(), expected_unicode)

    def test_outbound_messsages_creation_on_message_save(self):
        # si new message then x neew outbound TestMessages
        new_outbound_messages = OutboundMessage.objects.all()
        self.assertEquals(new_outbound_messages.count(), 2)


    def test_successful_send(self):
        outbound_message = OutboundMessage.objects.create(message = self.message, contact=self.contact1)
        result = outbound_message.send()

        self.assertTrue(result)
        outbound_message = OutboundMessage.objects.get(id=outbound_message.id)
        self.assertEquals(outbound_message.status, "sent")


    @skip("There should be a link between a message and a person that now does not exist")
    def test_it_should_create_an_output_message_for_person_without_contacts(self):
        person_without_contacts = Person.objects.create(api_instance=self.api_instance1, name= 'I don\'t have any contacts')
        message_to_3 = Message.objects.create(content = 'hello there', subject='Wow!', writeitinstance= self.writeitinstance1, persons = [self.person1,\
            self.person2, person_without_contacts])

        outbound_messages = OutboundMessage.objects.filter(message=message_to_3)
        self.assertEquals(outbound_messages.count(), 3)


    def test_there_is_a_manager_that_retrieves_all_the_available_messages(self):
        outbound_message = OutboundMessage.objects.create(message = self.message, contact=self.contact1)

        self.assertEquals(OutboundMessage.objects.to_send().filter(id=outbound_message.id).count(),1)


from mental_message_plugin import *
class PluginMentalMessageTestCase(TestCase):
    def setUp(self):
        super(PluginMentalMessageTestCase,self).setUp()
        self.outbound_message = OutboundMessage.objects.all()[0]
        self.message_type = ContentType.objects.all()[0]


    def test_it_has_a_send_method_and_does_whatever(self):
        the_mental_channel = MentalMessage()
        #it sends the message
        the_mental_channel.send(self.outbound_message)
        #And I'm gonna prove it by testing that a new record was created
        the_records = MessageRecord.objects.filter(object_id=self.outbound_message.id, status="sent using mental messages")
        self.assertEquals(the_records.count(),1)
        #It should send using all the channels available

    def test_it_should_create_a_new_kind_of_outbox_message(self):
        self.outbound_message.send()
        the_records = MessageRecord.objects.filter(object_id=self.outbound_message.id, status="sent using mental messages")
        self.assertEquals(the_records.count(),1)