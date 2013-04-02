from django.test import TestCase
from nuntium.plugins import OutputPlugin


class MentalMessage(OutputPlugin):
	name = 'mental-message'
	title = 'Mental Message'

class PluginsStructure(TestCase):
	def test_output_plugins(self):
		plugins = OutputPlugin.get_plugins()
		plugins_counter = 0

		for plugin in plugins:
			plugins_counter += 1

		self.assertEquals(plugins_counter, 1)