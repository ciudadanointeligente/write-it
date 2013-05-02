from global_test_case import GlobalTestCase as TestCase
from django.utils.unittest import skip
from nuntium.models import Message, WriteItInstance, OutboundMessage, MessageRecord, OutboundMessagePluginRecord
from plugin_mock.mental_message_plugin import MentalMessage, FatalException, TryAgainException
from djangoplugins.models import Plugin
from popit.models import Person
'''
This testcase is intented to test the OutboundMessageRecord model
and it's creation when sending an outbound_message, the calculation of
attempts and the status of the outbound_message at the end 

The class tested in this file has the responsability of recording to
what plugin an outbound message has been sent
'''

class OutboundMessageRecordTestCase(TestCase):
    def setUp(self):
        super(OutboundMessageRecordTestCase,self).setUp()
        self.person1 = Person.objects.all()[0]
        self.writeitinstance1 = WriteItInstance.objects.all()[0]


        self.fatal_error_message = Message.objects.create(content = 'Content 1', subject='RaiseFatalErrorPlz', 
            writeitinstance= self.writeitinstance1, persons = [self.person1])
        self.fatal_error_outboundmessage = OutboundMessage.objects.filter(message=self.fatal_error_message)[0]

        self.try_again_error_message = Message.objects.create(content = 'Content 1', subject='RaiseTryAgainErrorPlz', 
            writeitinstance= self.writeitinstance1, persons = [self.person1])
        self.try_again_outbound_message = OutboundMessage.objects.filter(message=self.try_again_error_message)[0]

        self.successful_message = Message.objects.create(content = 'Content 1', subject='Come on! send me!', 
            writeitinstance= self.writeitinstance1, persons = [self.person1])
        self.successful_outbound_message = OutboundMessage.objects.filter(message=self.successful_message)[0]
        self.channel = MentalMessage()
        self.plugin_model = self.channel.get_model()



    def test_create_new(self):
        record = OutboundMessagePluginRecord.objects.create(outbound_message=self.successful_outbound_message, 
            plugin=self.plugin_model, sent=True)
        self.assertTrue(record)
        self.assertEquals(record.outbound_message, self.successful_outbound_message)
        self.assertEquals(record.plugin, self.plugin_model)
        self.assertTrue(record.sent)
        self.assertEquals(record.number_of_attempts, 0)
        self.assertTrue(record.try_again)

    #I know this is not a scenario or something like that
    #but this is the first name that I came up with for this
    #test
    def test_successfully_sending_an_outbound_message(self):
        self.successful_outbound_message.send()

        record = OutboundMessagePluginRecord.objects.get(outbound_message=self.successful_outbound_message, 
            plugin=self.plugin_model)
        self.assertTrue(record.sent)
        self.assertEquals(record.number_of_attempts, 1)
        self.assertFalse(record.try_again)

    def test_fatal_error_in_sending(self):
        self.fatal_error_outboundmessage.send()
        record = OutboundMessagePluginRecord.objects.get(outbound_message=self.fatal_error_outboundmessage, 
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





