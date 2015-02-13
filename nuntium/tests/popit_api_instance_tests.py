# coding=utf-8
from global_test_case import GlobalTestCase as TestCase, popit_load_data
from nuntium.models import WriteItInstance
from contactos.models import Contact, ContactType
from django.utils.unittest import skipUnless
from django.conf import settings
from django.contrib.auth.models import User


@skipUnless(settings.LOCAL_POPIT, "No local popit running")
class EmailCreationWhenPullingFromPopit(TestCase):
    def setUp(self):
        super(EmailCreationWhenPullingFromPopit, self).setUp()
        self.instance = WriteItInstance.objects.all()[0]

    def test_it_pulls_and_creates_contacts(self):
        '''When pulling from popit it also creates emails'''

        popit_load_data(fixture_name='persons_with_emails')

        self.instance.load_persons_from_a_popit_api(
            settings.TEST_POPIT_API_URL
        )
        User.objects.create_user(username="perro", password="gato")
        fiera = self.instance.persons.filter(name="Fiera Feroz")
        # fiera should have at least one contact commig from popit
        contacts = Contact.objects.filter(person=fiera)
        self.assertTrue(contacts)
        contact = contacts[0]
        contact_type = ContactType.objects.get(name="e-mail")
        self.assertEquals(contact.contact_type, contact_type)
        self.assertEquals(contact.value, "fiera@ciudadanointeligente.org")
        self.assertEquals(contact.writeitinstance, self.instance)

    def test_it_does_not_replicate_contacts(self):
        '''It does not replicate a contact several times'''
        popit_load_data(fixture_name='persons_with_emails')

        self.instance.load_persons_from_a_popit_api(
            settings.TEST_POPIT_API_URL
        )
        self.instance.load_persons_from_a_popit_api(
            settings.TEST_POPIT_API_URL
        )
        User.objects.create_user(username="perro", password="gato")
        fiera = self.instance.persons.filter(name="Fiera Feroz")
        # fiera should have at least one contact commig from popit
        contacts = Contact.objects.filter(person=fiera)
        self.assertEquals(contacts.count(), 1)

    def test_not_replicate_contact_even_if_value_changes(self):
        '''The value of an email has changed in popit but in writeit it should just update the value'''
        # Creating and loading the data
        popit_load_data(fixture_name='persons_with_emails')

        self.instance.load_persons_from_a_popit_api(
            settings.TEST_POPIT_API_URL
        )

        # Updating the data and loading again
        popit_load_data(fixture_name='persons_with_emails2')

        self.instance.load_persons_from_a_popit_api(
            settings.TEST_POPIT_API_URL
        )

        fiera = self.instance.persons.filter(name="Fiera Feroz")
        contacts = Contact.objects.filter(person=fiera)
        self.assertEquals(contacts.count(), 1)

    def test_get_emails_in_the_popolo_format(self):
        '''Get emails contact if it comes in the popolo format'''

        popit_load_data(fixture_name='other_people_with_popolo_emails')

        self.instance.load_persons_from_a_popit_api(
            settings.TEST_POPIT_API_URL
        )
        fiera = self.instance.persons.filter(name="Fiera Feroz")
        # fiera should have at least one contact commig from popit
        contacts = Contact.objects.filter(person=fiera)
        self.assertTrue(contacts)
        contact = contacts[0]
        contact_type = ContactType.objects.get(name="e-mail")
        self.assertEquals(contact.contact_type, contact_type)
        self.assertEquals(contact.value, "fiera-popolo@ciudadanointeligente.org")

    def test_get_twice_from_popit_does_not_repeat_the_email(self):
        '''Ít does not duplicate emails if they are comming in the field preferred email'''
        popit_load_data(fixture_name='other_people_with_popolo_emails')

        self.instance.load_persons_from_a_popit_api(
            settings.TEST_POPIT_API_URL
        )
        self.instance.load_persons_from_a_popit_api(
            settings.TEST_POPIT_API_URL
        )
        fiera = self.instance.persons.filter(name="Fiera Feroz")
        contacts = Contact.objects.filter(person=fiera)
        self.assertEquals(contacts.count(), 1)

    def atest_bug_506(self):
        '''If the same email is in preferred email and
        in the list of contact_details it creates a single one'''
        popit_load_data(fixture_name='person_with_preferred_email_and_contact_detail')

        self.instance.load_persons_from_a_popit_api(
            settings.TEST_POPIT_API_URL
        )

        fiera = self.instance.persons.filter(name="Fiera Feroz")
        contacts = Contact.objects.filter(person=fiera)
        self.assertEquals(contacts.count(), 1)
        # I'm prefering the one with popit_id and stuff
        the_contact = contacts[0]
        self.assertTrue(the_contact.popit_identifier)
