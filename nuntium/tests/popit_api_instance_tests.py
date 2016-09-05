# coding=utf-8
from datetime import datetime
from mock import patch

from global_test_case import GlobalTestCase as TestCase, popit_load_data
from instance.models import WriteItInstance, today_in_date_range
from contactos.models import Contact, ContactType
from django.conf import settings
from django.contrib.auth.models import User


class EmailCreationWhenPullingFromPopit(TestCase):
    def setUp(self):
        super(EmailCreationWhenPullingFromPopit, self).setUp()
        self.instance = WriteItInstance.objects.get(id=1)

    @popit_load_data(fixture_name='persons_with_emails')
    def test_it_pulls_and_creates_contacts(self):
        '''When pulling from popit it also creates emails'''

        self.instance.load_persons_from_popolo_json(
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

    @popit_load_data(fixture_name='persons_with_emails')
    def test_it_does_not_replicate_contacts(self):
        '''It does not replicate a contact several times'''
        self.instance.load_persons_from_popolo_json(
            settings.TEST_POPIT_API_URL
        )
        self.instance.load_persons_from_popolo_json(
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
        with popit_load_data(fixture_name='persons_with_emails'):
            self.instance.load_persons_from_popolo_json(
                settings.TEST_POPIT_API_URL
            )

        # Updating the data and loading again
        with popit_load_data(fixture_name='persons_with_emails2'):
            self.instance.load_persons_from_popolo_json(
                settings.TEST_POPIT_API_URL
            )

        fiera = self.instance.persons.filter(name="Fiera Feroz")
        contacts = Contact.objects.filter(person=fiera)
        self.assertEquals(contacts.count(), 1)

    @popit_load_data(fixture_name='other_people_with_popolo_emails')
    def test_get_emails_in_the_popolo_format(self):
        '''Get emails contact if it comes in the popolo format'''
        self.instance.load_persons_from_popolo_json(
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

    @popit_load_data(fixture_name='other_people_with_popolo_emails')
    def test_get_twice_from_popit_does_not_repeat_the_email(self):
        '''Ít does not duplicate emails if they are comming in the field preferred email'''
        self.instance.load_persons_from_popolo_json(
            settings.TEST_POPIT_API_URL
        )
        self.instance.load_persons_from_popolo_json(
            settings.TEST_POPIT_API_URL
        )
        fiera = self.instance.persons.filter(name="Fiera Feroz")
        contacts = Contact.objects.filter(person=fiera)
        self.assertEquals(contacts.count(), 1)

    @popit_load_data(fixture_name='persons_with_null_values')
    def test_accept_null_values(self):
        '''It can process information that has null values'''
        self.instance.load_persons_from_popolo_json(
            settings.TEST_POPIT_API_URL
        )
        fiera = self.instance.persons.get(name="Fiera Feroz")
        self.assertFalse(Contact.objects.filter(person=fiera))

    @popit_load_data(fixture_name='person_with_preferred_email_and_contact_detail')
    def test_bug_506(self):
        '''If the same email is in preferred email and
        in the list of contact_details it creates a single one'''
        self.instance.load_persons_from_popolo_json(
            settings.TEST_POPIT_API_URL
        )

        fiera = self.instance.persons.filter(name="Fiera Feroz")
        contacts = Contact.objects.filter(person=fiera)
        self.assertEquals(contacts.count(), 1)
        # I'm prefering the one with popit_id and stuff
        the_contact = contacts[0]
        self.assertTrue(the_contact.popit_identifier)

    @popit_load_data(fixture_name='persons_with_memberships')
    def test_if_memberships_are_no_longer_active(self):
        '''
        If all memberships are no longer active then the
        contacts should be disabled.
        Related to #419.
        '''
        with patch('instance.models.datetime') as mock_datetime:
            mock_datetime.date.today.return_value = datetime(2015, 1, 1)

            self.instance.load_persons_from_popolo_json(
                settings.TEST_POPIT_API_URL
            )
            # Benito was the boss between 1987-03-21
            # and 2007-03-20
            benito = self.instance.persons.get(name="Benito")
            contacts = Contact.objects.filter(person=benito)
            self.assertFalse(contacts.filter(enabled=True))

            # Fiera has been the boss since 2011-03-21
            # And she was the boss of another NGO before between 2005-03-21
            # and 2009-03-21
            fiera = self.instance.persons.get(name="Fiera Feroz")
            contacts = Contact.objects.filter(person=fiera)
            self.assertTrue(contacts.filter(enabled=True))

            # raton has been the noboss between 1987-03-21 and
            # will keep on being until 2045-03-20
            raton = self.instance.persons.get(name="Ratón Inteligente")
            contacts = Contact.objects.filter(person=raton)
            self.assertTrue(contacts.filter(enabled=True))

class IsActiveTestCase(TestCase):
    def test_validating_if_a_membership_is_active(self):
        with patch('instance.models.datetime') as mock_datetime:
            mock_datetime.date.today.return_value = datetime(2000, 1, 1)

            far_past = datetime(1900, 1, 1)
            past = datetime(1999, 1, 1)
            future = datetime(2020, 1, 1)
            far_future = datetime(2525, 1, 1)

            self.assertFalse(today_in_date_range(far_past, past))
            self.assertFalse(today_in_date_range(None, past))
            self.assertTrue(today_in_date_range(past, None))
            self.assertTrue(today_in_date_range(past, future))
            self.assertTrue(today_in_date_range(None, future))
            self.assertFalse(today_in_date_range(future, far_future))

            # Handles empty strings as dates
            self.assertTrue(today_in_date_range(past, None))

            # If there's neither a start date or an end date, that's current.
            self.assertTrue(today_in_date_range(None, None))
