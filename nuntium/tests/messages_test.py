from django.test import TestCase
from nuntium.models import Message, WriteItInstance, OutboundMessage
from contactos.models import Contact, ContactType
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from popit.models import Person, ApiInstance

class TestMessages(TestCase):

    def setUp(self):
        self.api_instance1 = ApiInstance.objects.create(url='http://popit.org/api/v1')
        self.api_instance2 = ApiInstance.objects.create(url='http://popit.org/api/v2')
        self.person1 = Person.objects.create(api_instance=self.api_instance1, name= 'Person 1')
        self.contact_type1 = ContactType.objects.create(name= 'e-mail',label_name='Electronic Mail')
        self.contact1 = Contact.objects.create(person=self.person1, contact_type=self.contact_type1, value= 'test@test.com')
        self.writeitinstance1 = WriteItInstance.objects.create(name='instance 1', api_instance= self.api_instance1)

    def test_create_message(self):
        
        message = Message.objects.create(content = 'Content 1', subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])
        self.assertTrue(message)

        #self.assertEquals(message.outboundmessage_set.count(), 1)
        #Validation test pending
        # self.assertRaises(ValidationError, Message, content='Content') # subject missing
        # self.assertRaises(ValidationError, Message, subject = 'Subject') # url missing


    def test_outboundmessage_create_without_manager(self):
        message = Message(content = 'Content 1', subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])
        message.save()

        
        self.assertEquals(message.outboundmessage_set.count(), 1)






    def test_it_raises_typeerror_when_no_contacts_are_present(self):

        try:
            Message.objects.create(content = 'Content 1', subject='Subject 1', writeitinstance= self.writeitinstance1)
        except TypeError as error:
            self.assertEquals(str(error),'A message needs persons to be sent')




class OutboundMessageTestCase(TestCase):
    def setUp(self):
        self.api_instance1 = ApiInstance.objects.create(url='http://popit.org/api/v1')
        self.person1 = Person.objects.create(api_instance=self.api_instance1, name= 'Person 1')
        self.person2 = Person.objects.create(api_instance=self.api_instance1, name= 'Person 2')
        self.contact_type1 = ContactType.objects.create(name= 'e-mail',label_name='Electronic Mail')
        self.contact1 = Contact.objects.create(person=self.person1, contact_type=self.contact_type1, value= 'test@test.com')
        self.contact2 = Contact.objects.create(person=self.person2, contact_type=self.contact_type1, value= 'test@test.com')
        self.writeitinstance1 = WriteItInstance.objects.create(name='instance 1', api_instance= self.api_instance1)
        self.message = Message.objects.create(content = 'Content 1', subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1,\
            self.person2])


    def test_create_a_outbound_message(self):
        outbound_message = OutboundMessage.objects.create(message = self.message, contact=self.contact1)
        #This means that there is a link between a contact and a message
        self.assertTrue(outbound_message)

    def test_outbound_messsages_creation_on_message_save(self):
        # si new message then x neew outbound TestMessages
        new_outbound_messages = OutboundMessage.objects.all()
        self.assertEquals(new_outbound_messages.count(), 2)






