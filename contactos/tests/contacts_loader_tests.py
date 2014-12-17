from global_test_case import GlobalTestCase as TestCase
from popit.models import Person
from ..models import Contact, ContactType
from django.contrib.auth.models import User
from django.core.management import call_command


class ContactsLoaderTestCase(TestCase):
    def setUp(self):
        super(ContactsLoaderTestCase, self).setUp()
        self.peter = Person.objects.all()[0]
        self.peter.contact_set.all().delete()
        self.owner = User.objects.create(username='jime')

    def test_add_contact(self):
        self.assertFalse(self.peter.contact_set.all())

        command_name = 'contacts_loader'
        owner_name = 'jime'
        contact_type_name = 'e-mail'
        file_path = 'contactos/tests/fixtures/contacts.csv'
        call_command(command_name, owner_name, contact_type_name, file_path, verbosity=0)

        contact = Contact.objects.get(person=self.peter)
        self.assertTrue(contact, self.peter)
        self.assertEquals(contact.value, 'pdaire@pdaire.org')
        owner = User.objects.get(username=owner_name)
        self.assertEquals(contact.owner, owner)
        contact_type = ContactType.objects.get(name=contact_type_name)
        self.assertEquals(contact.contact_type, contact_type)
