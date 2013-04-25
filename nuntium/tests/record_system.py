from django.test import TestCase
from django.utils.unittest import skip
from nuntium.models import Message, WriteItInstance, OutboundMessage, MessageRecord
from django.contrib.contenttypes.models import ContentType
from popit.models import Person, ApiInstance
from contactos.models import Contact, ContactType
import datetime


class MessageRecordTestCase(TestCase):
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
        self.message_type = ContentType.objects.get(app_label="nuntium", model="message")

    def test_create_a_record(self):
        record = MessageRecord.objects.create(content_object= self.message, status="something")
        

        self.assertEquals(record.content_type, self.message_type)
        self.assertEquals(record.object_id, self.message.id)
        self.assertEquals(record.status, "something")
        self.assertEquals(record.datetime.date(), datetime.datetime.today().date() )


    def test_creates_a_record_when_creating_a_message(self):
        message1 = Message.objects.create(content = 'Content 1', subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1,\
            self.person2])

        the_records = MessageRecord.objects.filter(content_type=self.message_type, object_id=message1.id, status="new")

        self.assertEquals(the_records.count(), 1) #the message has been created

        the_record = the_records[0]
        self.assertEquals(the_record.status, "new")


    def test_creates_a_record_when_sending_a_message(self):
        message1 = Message.objects.create(content = 'Content 1', subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1,\
            self.person2])
        message1.send()

        the_records = MessageRecord.objects.filter(content_type=self.message_type, object_id=message1.id, status="sent")

        self.assertEquals(the_records.count(), 1) #the message has been created


    def test_it_is_created_only_once_on_message_sending(self):
        message1 = Message.objects.create(content = 'Content 1', subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1,\
            self.person2])
        message1.send()
        message1.save()

        the_records = MessageRecord.objects.filter(content_type=self.message_type, object_id=message1.id, status="sent")
        self.assertEquals(the_records.count(), 1) #the message has been created





