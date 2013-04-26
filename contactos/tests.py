from global_test_case import GlobalTestCase as TestCase
from django.utils.unittest import skip
from contactos.models import ContactType, Contact
from popit.models import Person, ApiInstance

class ContactTestCase(TestCase):
    def setUp(self):
        super(ContactTestCase,self).setUp()
        self.person = Person.objects.all()[0]

    def test_create_contact_type(self):
        contact_type = ContactType.objects.create(name='mental message', label_name = 'mental address id')
        self.assertTrue(contact_type)
        self.assertEquals(contact_type.name, 'mental message')
        self.assertEquals(contact_type.label_name, 'mental address id')

    def test_create_contact(self):
        contact_type = ContactType.objects.create(name='mental message', label_name = 'mental address id')
        contact1 = Contact.objects.create(contact_type= contact_type, value = 'contact point', person= self.person)
        self.assertTrue(contact1)