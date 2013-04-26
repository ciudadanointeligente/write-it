from global_test_case import GlobalTestCase as TestCase
from nuntium.plugins import OutputPlugin

from contactos.models import Contact, ContactType



class PluginsStructure(TestCase):
    def setUp(self):
    	super(PluginsStructure,self).setUp()
        from mental_message_plugin import MentalMessage


    def test_output_plugins(self):
        plugins = OutputPlugin.get_plugins()
        plugin_names = []

        for plugin in plugins:
            plugin_names.append(plugin.name)


        self.assertTrue("mental-message" in plugin_names)