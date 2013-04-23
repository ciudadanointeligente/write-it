from django.test import TestCase
from nuntium.plugins import OutputPlugin

from contactos.models import Contact, ContactType



class PluginsStructure(TestCase):
    def setUp(self):
        from mental_message_plugin import MentalMessage


    def test_output_plugins(self):
        plugins = OutputPlugin.get_plugins()
        plugins_counter = 0

        for plugin in plugins:
            plugins_counter += 1

        self.assertEquals(plugins_counter, 1)