from djangoplugins.point import PluginPoint
from contactos.models import ContactType

class OutputPlugin(PluginPoint):
    def get_contact_type(self):
        contact_type, created = ContactType.objects.get_or_create(label_name=self.title, name=self.name)
        return contact_type