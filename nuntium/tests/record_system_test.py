from global_test_case import GlobalTestCase as TestCase
from instance.models import WriteItInstance
from ..models import Message, OutboundMessage, MessageRecord
from django.contrib.contenttypes.models import ContentType
from popolo.models import Person
from django.utils.translation import ugettext as _
import datetime


class MessageRecordTestCase(TestCase):
    def setUp(self):
        super(MessageRecordTestCase, self).setUp()
        self.outboundmessage_type = ContentType.objects.get(model="outboundmessage")
        self.writeitinstance1 = WriteItInstance.objects.get(id=1)
        self.outbound_message = OutboundMessage.objects.get(id=1)
        self.person1 = Person.objects.get(id=1)
        self.person2 = Person.objects.get(id=2)

    def test_create_a_record(self):
        record = MessageRecord.objects.create(
            content_object=self.outbound_message, status="something")

        self.assertEquals(record.content_type, self.outboundmessage_type)
        self.assertEquals(record.object_id, self.outbound_message.id)
        self.assertEquals(record.status, "something")
        self.assertEquals(record.datetime.date(), datetime.datetime.utcnow().date())

    def test_record_unicode(self):
        record = MessageRecord.objects.create(
            content_object=self.outbound_message, status="something")
        expected_unicode = _('The message "%(subject)s" at %(instance)s turned %(status)s at %(date)s') % {
            'subject': self.outbound_message.message.subject,
            'instance': self.writeitinstance1,
            'status': record.status,
            'date': str(record.datetime),
            }
        self.assertEquals(record.__unicode__(), expected_unicode)

    def test_creates_a_record_when_creating_a_message(self):
        # Person 1 and person 2 have a contact each one and therefore
        # There should be created a new record for the creation of
        # outbound messages to each of those contacts
        message1 = Message.objects.create(
            content='Content 1',
            subject='Subject 1',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1, self.person2],
            )
        outbound_messages = OutboundMessage.objects.filter(message=message1)

        the_records = MessageRecord.objects.filter(content_type=self.outboundmessage_type, object_id__in=outbound_messages)

        self.assertEquals(the_records.count(), 2)  # the message has been created

        the_record = the_records[0]
        self.assertEquals(the_record.status, "new")

        # TODO: The default status should be new but for now because we don't yet have the confirmation email
        # flow it is going to be ready

    def test_creates_a_record_when_sending_an_outbound_message(self):
        message1 = Message.objects.create(
            content='Content 1',
            subject='Subject 1',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1, self.person2],
            )
        outbound_messages = OutboundMessage.objects.filter(message=message1)
        first_outbound_message = outbound_messages[0]
        first_outbound_message.send()

        the_records = MessageRecord.objects.filter(content_type=self.outboundmessage_type, object_id=first_outbound_message.id, status="sent")

        self.assertEquals(the_records.count(), 1)  # the message has been created

    def test_it_is_created_only_once_on_message_sending(self):
        message1 = Message.objects.create(
            content='Content 1',
            subject='Subject 1',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1, self.person2],
            )
        outbound_messages = OutboundMessage.objects.filter(message=message1)
        first_outbound_message = outbound_messages[0]
        first_outbound_message.send()
        first_outbound_message.send()

        the_records = MessageRecord.objects.filter(content_type=self.outboundmessage_type, object_id=first_outbound_message.id, status="sent")
        self.assertEquals(the_records.count(), 1)  # the message has been created
