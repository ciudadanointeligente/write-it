'''
The class tested in this file has the responsability of recording to what plugin an outbound message has been sent
'''
from global_test_case import GlobalTestCase as TestCase
from django.utils.unittest import skip
from nuntium.models import Message, WriteItInstance, OutboundMessage, MessageRecord, OutboundMessagePluginRecord
from plugin_mock.mental_message_plugin import MentalMessage, FatalException, TryAgainException
from djangoplugins.models import Plugin


class OutboundMessageRecordTestCase(TestCase):
	def setUp(self):
		super(OutboundMessageRecordTestCase,self).setUp()
		self.outbound_message = OutboundMessage.objects.all()[0]
		self.channel = MentalMessage()
		self.plugin_model = self.channel.get_model()


	def test_create_new(self):
		record = OutboundMessagePluginRecord.objects.create(outbound_message=self.outbound_message, 
			plugin=self.plugin_model, sent=True)
		self.assertTrue(record)
		self.assertEquals(record.outbound_message, self.outbound_message)
		self.assertEquals(record.plugin, self.plugin_model)
		self.assertTrue(record.sent)