from global_test_case import GlobalTestCase as TestCase
from django.utils.unittest import skip
from nuntium.models import Message, WriteItInstance, OutboundMessage, MessageRecord
from django.contrib.contenttypes.models import ContentType
from popit.models import Person, ApiInstance
from contactos.models import Contact, ContactType
import datetime


class MessageRecordTestCase(TestCase):
    def setUp(self):
        super(MessageRecordTestCase,self).setUp()
        self.message = Message.objects.all()[0]
        self.message_type = ContentType.objects.get(app_label="nuntium", model="message")
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.person1 = Person.objects.all()[0]
        self.person2 = Person.objects.all()[1]

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





