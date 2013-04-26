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
        message = Message.objects.create(content = 'Content 1', subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])
        self.assertTrue(message)
        self.assertEquals(message.content, "Content 1")
        self.assertEquals(message.subject, "Subject 1")
        self.assertEquals(message.writeitinstance, self.writeitinstance1)
        self.assertEquals(message.status, "new")

    def test_message_unicode(self):
        message = Message.objects.create(content = 'Content 1', subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])

        self.assertEquals(message.__unicode__(), _('%(subject)s at %(instance)s') % {
            'subject':message.subject,
            'instance':self.writeitinstance1.name
            })

    def test_outboundmessage_create_without_manager(self):
        message = Message(content = 'Content 1', subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])
        message.save()

        
        self.assertEquals(message.outboundmessage_set.count(), 1)


    def test_it_creates_outbound_messages_only_once(self):
        message = Message.objects.create(content = 'Content 1', subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])
        message.save()

        self.assertEquals(OutboundMessage.objects.filter(message=message).count(), 1)

    def test_it_raises_typeerror_when_no_contacts_are_present(self):

        try:
            Message.objects.create(content = 'Content 1', subject='Subject 1', writeitinstance= self.writeitinstance1)
        except TypeError as error:
            self.assertEquals(str(error),'A message needs persons to be sent')

    def test_when_a_message_is_sent_it_changes_its_status(self):
        message = Message.objects.create(content = 'Content 1', subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])
        sent = message.send()
        message = Message.objects.get(id=message.id)

        self.assertTrue(sent)
        self.assertEquals(message.status, "sent")

    def test_it_does_not_send_a_message_twice(self):
        message = Message.objects.create(content = 'Content 1', subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])
        first_time = message.send()
        second_time = message.send()

        #Once again we should have a logging system, the tests
        #are getting hard to write

        self.assertFalse(second_time)


    def test_manager_has_a_method_to_retrieve_to_send_messages(self):
        message1 = Message.objects.all()[0]
        message2 = Message.objects.all()[1]

        message1.send()

        self.assertEquals(Message.objects.to_send().count(), 1)#message2 that has not been sent yet
        self.assertEquals(Message.objects.to_send()[0], message2)


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

    def test_outbound_messsages_creation_on_message_save(self):
        # si new message then x neew outbound TestMessages
        new_outbound_messages = OutboundMessage.objects.all()
        self.assertEquals(new_outbound_messages.count(), 2)

    @skip("There should be a link between a message and a person that now does not exist")
    def test_it_should_create_an_output_message_for_person_without_contacts(self):
        person_without_contacts = Person.objects.create(api_instance=self.api_instance1, name= 'I don\'t have any contacts')
        message_to_3 = Message.objects.create(content = 'hello there', subject='Wow!', writeitinstance= self.writeitinstance1, persons = [self.person1,\
            self.person2, person_without_contacts])

        outbound_messages = OutboundMessage.objects.filter(message=message_to_3)
        self.assertEquals(outbound_messages.count(), 3)


from mental_message_plugin import *
class PluginMentalMessageTestCase(TestCase):
    def setUp(self):
        super(PluginMentalMessageTestCase,self).setUp()
        self.message = Message.objects.all()[0]
        self.message_type = ContentType.objects.all()[0]


    def test_it_has_a_send_method_and_does_whatever(self):
        the_mental_channel = MentalMessage()
        #it sends the message
        the_mental_channel.send(self.message)
        #And I'm gonna prove it by testing that a new record was created
        the_records = MessageRecord.objects.filter(object_id=self.message.id, status="sent using mental messages")
        self.assertEquals(the_records.count(),1)
    #It should send using all the channels available
    def test_it_should_create_a_new_kind_of_outbox_message(self):
        self.message.send()
        the_records = MessageRecord.objects.filter(object_id=self.message.id, status="sent using mental messages")
        self.assertEquals(the_records.count(),1)