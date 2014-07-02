from global_test_case import GlobalTestCase as TestCase
from contactos.models import ContactType
from .. import ManualChannel
from nuntium.plugins import OutputPlugin

class ManualPluginTestCase(TestCase):
	def setUp(self):
		super(ManualPluginTestCase, self).setUp()

	def test_instanciate_the_plugin(self):
		'''Instanciate the manual plugin'''
		channel = ManualChannel()
		self.assertTrue(channel)
		self.assertIsInstance(channel, OutputPlugin)


	def test_it_has_a_contact_type(self):
		'''It has a manual contact type'''
		channel = ManualChannel()
		contact_type = channel.get_contact_type()
		self.assertIsInstance(contact_type, ContactType)
		self.assertEquals(contact_type.label_name, "Manual Contact")
		self.assertEquals(contact_type.name, "manual")


	def test_has_a_send_method(self):
		'''It does have a send method'''
		channel = ManualChannel()
		self.assertTrue(channel.send)

