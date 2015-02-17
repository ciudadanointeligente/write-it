# coding=utf-8
from global_test_case import GlobalTestCase as TestCase, popit_load_data
from ..user_section.forms import WriteItInstanceCreateFormPopitUrl, SimpleInstanceCreateFormPopitUrl
from django.utils.unittest import skipUnless
from django.contrib.auth.models import User
from django.conf import settings
from mock import patch


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
        self.assertNotIn("moderation_needed_in_all_messages", form.fields)
        self.assertIn("owner", form.fields)
        self.assertNotIn("allow_messages_using_form", form.fields)
        self.assertNotIn("rate_limiter", form.fields)
        self.assertNotIn("notify_owner_when_new_answer", form.fields)
        self.assertNotIn("autoconfirm_api_messages", form.fields)

    def test_it_uses_popit_main_url_as_well(self):
        '''It accepts main popit url as well'''
        with patch('nuntium.models.WriteItInstance.load_persons_from_a_popit_api') as method_load:
            data = {
                'owner': self.user.id,
                'popit_url': 'https://kenyan-politicians.popit.mysociety.org/',
                'name': "instance",
                "rate_limiter": 0,
            }
            form = WriteItInstanceCreateFormPopitUrl(data)
            form.save()
            method_load.assert_called_with('https://kenyan-politicians.popit.mysociety.org/api/v0.1')


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
