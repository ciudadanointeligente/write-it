from global_test_case import GlobalTestCase as TestCase
from instance.models import WriteItInstance
from ..models import Message, OutboundMessage, OutboundMessagePluginRecord
from plugin_mock.mental_message_plugin import MentalMessage
from contactos.models import Contact
# from djangoplugins.models import Plugin
from django.contrib.auth.models import User
from popolo.models import Person
'''
This testcase is intented to test the OutboundMessageRecord model
and it's creation when sending an outbound_message, the calculation of
attempts and the status of the outbound_message at the end

The class tested in this file has the responsability of recording to
what plugin an outbound message has been sent
'''


class OutboundMessageRecordTestCase(TestCase):
    def setUp(self):
        super(OutboundMessageRecordTestCase, self).setUp()
        self.channel = MentalMessage()

        self.person1 = Person.objects.get(id=1)
        self.user = User.objects.get(id=1)
        self.writeitinstance1 = WriteItInstance.objects.get(id=1)
        self.mental_contact1 = Contact.objects.create(
            person=self.person1,
            contact_type=self.channel.get_contact_type(),
            writeitinstance=self.writeitinstance1
        )

        self.fatal_error_message = Message.objects.create(
            content='Content 1',
            subject='RaiseFatalErrorPlz',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        self.fatal_error_outboundmessage = OutboundMessage.objects.get(message=self.fatal_error_message,
            contact=self.mental_contact1)

        self.try_again_error_message = Message.objects.create(
            content='Content 1',
            subject='RaiseTryAgainErrorPlz',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        self.try_again_outbound_message = OutboundMessage.objects.get(message=self.try_again_error_message,
            contact=self.mental_contact1)

        self.successful_message = Message.objects.create(
            content='Content 1',
            subject='Come on! send me!',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        self.successful_outbound_message = OutboundMessage.objects.get(message=self.successful_message,
            contact=self.mental_contact1)
        self.channel = MentalMessage()
        self.plugin_model = self.channel.get_model()

    def test_create_new(self):
        record = OutboundMessagePluginRecord.objects.create(
            outbound_message=self.successful_outbound_message,
            plugin=self.plugin_model,
            sent=True)
        self.assertTrue(record)
        self.assertEquals(record.outbound_message, self.successful_outbound_message)
        self.assertEquals(record.plugin, self.plugin_model)
        self.assertTrue(record.sent)
        self.assertEquals(record.number_of_attempts, 0)
        self.assertTrue(record.try_again)

    # I know this is not a scenario or something like that
    # but this is the first name that I came up with for this test
    def test_successfully_sending_an_outbound_message(self):
        self.successful_outbound_message.send()

        record = OutboundMessagePluginRecord.objects.get(
            outbound_message=self.successful_outbound_message,
            plugin=self.plugin_model)
        self.assertTrue(record.sent)
        self.assertEquals(record.number_of_attempts, 1)
        self.assertFalse(record.try_again)

    def test_fatal_error_in_sending(self):
        self.fatal_error_outboundmessage.send()
        record = OutboundMessagePluginRecord.objects.get(
            outbound_message=self.fatal_error_outboundmessage,
            plugin=self.plugin_model)

        self.assertFalse(record.sent)
        self.assertEquals(record.number_of_attempts, 1)
        self.assertFalse(record.try_again)

    def test_non_fatal_error_in_sending(self):
        self.try_again_outbound_message.send()
        record = OutboundMessagePluginRecord.objects.get(outbound_message=self.try_again_outbound_message,
            plugin=self.plugin_model)

        self.assertFalse(record.sent)
        self.assertEquals(record.number_of_attempts, 1)
        self.assertTrue(record.try_again)

    def test_it_does_not_create_a_new_record_when_sending_again(self):
        self.try_again_outbound_message.send()
        record = OutboundMessagePluginRecord.objects.get(outbound_message=self.try_again_outbound_message,
            plugin=self.plugin_model)

        self.try_again_outbound_message.send()

        record = OutboundMessagePluginRecord.objects.get(outbound_message=self.try_again_outbound_message,
            plugin=self.plugin_model)

        self.assertFalse(record.sent)
        self.assertEquals(record.number_of_attempts, 2)
        self.assertTrue(record.try_again)

    def test_it_should_not_send_again_when_it_says_do_not_send_me(self):
        self.fatal_error_outboundmessage.send()
        self.fatal_error_outboundmessage.send()
        record = OutboundMessagePluginRecord.objects.get(outbound_message=self.fatal_error_outboundmessage,
            plugin=self.plugin_model)

        self.assertEquals(record.number_of_attempts, 1)
