# coding=utf-8
from global_test_case import GlobalTestCase as TestCase, popit_load_data
from ..user_section.forms import WriteItInstanceCreateFormPopitUrl, SimpleInstanceCreateFormPopitUrl
from django.utils.unittest import skipUnless
from django.contrib.auth.models import User
from django.conf import settings
from nuntium.models import WriteItInstance
from contactos.models import Contact, ContactType


@skipUnless(settings.LOCAL_POPIT, "No local popit running")
class InstanceCreateFormTestCase(TestCase):
    def setUp(self):
        super(InstanceCreateFormTestCase, self).setUp()
        self.user = User.objects.first()

    def test_instanciate_the_form(self):
        '''Instanciate the form for creating a writeit instance'''
        data = {
            'owner': self.user.id,
            'popit_url': settings.TEST_POPIT_API_URL,
            'name': "instance",
            "rate_limiter": 0,
            }
        form = WriteItInstanceCreateFormPopitUrl(data)

        self.assertTrue(form)
        self.assertTrue(form.is_valid())

    def test_creating_an_instance(self):
        '''Create an instance of writeit using a form that contains a popit_url'''
        # We have a popit running locally using the
        # start_local_popit_api.bash script
        popit_load_data()
        # loading data into the popit-api

        data = {
            'owner': self.user.id,
            'popit_url': settings.TEST_POPIT_API_URL,
            'name': "instance",
            "rate_limiter": 0,
            }
        form = WriteItInstanceCreateFormPopitUrl(data)
        instance = form.save()
        self.assertTrue(instance.persons.all())

    def test_creating_an_instance_without_popit_url(self):
        data = {
            'owner': self.user.id,
            'name': "instance",
            "rate_limiter": 0,
            }
        form = WriteItInstanceCreateFormPopitUrl(data)
        instance = form.save()

        self.assertFalse(instance.persons.all())

    def test_it_has_all_the_fields(self):
        """The form for creating a new writeit instance has all the fields"""
        form = WriteItInstanceCreateFormPopitUrl()

        self.assertIn("name", form.fields)
        self.assertNotIn("slug", form.fields)
        self.assertNotIn("persons", form.fields)
        self.assertIn("moderation_needed_in_all_messages", form.fields)
        self.assertIn("owner", form.fields)
        self.assertIn("allow_messages_using_form", form.fields)
        self.assertIn("rate_limiter", form.fields)
        self.assertIn("notify_owner_when_new_answer", form.fields)
        self.assertIn("autoconfirm_api_messages", form.fields)


class BasicInstanceCreateFormTestCase(TestCase):
    def setUp(self):
        super(BasicInstanceCreateFormTestCase, self).setUp()

    def test_the_form_is_a_subclass_of_the_more_complicated_version(self):
        '''This form is a subclass of the more confirmation verions'''

        form = SimpleInstanceCreateFormPopitUrl()
        self.assertIsInstance(form, WriteItInstanceCreateFormPopitUrl)

    def test_fields(self):
        '''The simple form for creating writeit instances contains the correct fields'''
        form = SimpleInstanceCreateFormPopitUrl()
        self.assertIn("name", form.fields)
        self.assertNotIn("slug", form.fields)
        self.assertNotIn("persons", form.fields)
        self.assertNotIn("moderation_needed_in_all_messages", form.fields)
        self.assertIn("owner", form.fields)
        self.assertNotIn("allow_messages_using_form", form.fields)
        self.assertNotIn("rate_limiter", form.fields)
        self.assertNotIn("notify_owner_when_new_answer", form.fields)
        self.assertNotIn("autoconfirm_api_messages", form.fields)


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
