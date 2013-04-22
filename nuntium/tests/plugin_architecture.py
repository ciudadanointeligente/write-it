from django.test import TestCase
from nuntium.plugins import OutputPlugin
from mental_message_plugin import MentalMessage
from contactos.models import Contact, ContactType



class PluginsStructure(TestCase):
    def test_output_plugins(self):
        plugins = OutputPlugin.get_plugins()
        plugins_counter = 0

        for plugin in plugins:
            plugins_counter += 1

        self.assertEquals(plugins_counter, 1)
        
    # def test_it_loads_a_contact_type(self):
    #     contacts = ContactType.objects.filter(name='mental-message', label_name='Mental Message')

    #     self.assertEquals(contacts.count(), 1)