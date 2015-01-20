from global_test_case import GlobalTestCase as TestCase
from ..plugins import OutputPlugin


class PluginsStructure(TestCase):
    def setUp(self):
        super(PluginsStructure, self).setUp()
        from plugin_mock.mental_message_plugin import MentalMessage  # noqa

    def test_output_plugins(self):
        plugins = OutputPlugin.get_plugins()
        plugin_names = []

        for plugin in plugins:
            plugin_names.append(plugin.name)

        self.assertTrue("mental-message" in plugin_names)


class OutputPluginTestCase(TestCase):
    def setUp(self):
        pass

    def test_it_returns_contact_type(self):
        plugin = OutputPlugin()
        plugin.name = "name"
        plugin.title = "The title thing"
        contact_type = plugin.get_contact_type()

        self.assertEquals(contact_type.name, plugin.name)
        self.assertEquals(contact_type.label_name, plugin.title)
