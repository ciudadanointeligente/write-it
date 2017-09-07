# -*- coding: utf-8 -*-
from django.core.management import call_command
from instance.models import WriteItInstance
from tastypie.test import ResourceTestCase, TestApiClient
from django.contrib.auth.models import User
from popolo.models import Person


class PersonResourceTestCase(ResourceTestCase):
    def setUp(self):
        super(PersonResourceTestCase, self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.user = User.objects.get(id=1)
        self.writeitinstance = WriteItInstance.objects.create(name=u"a test", slug=u"a-test", owner=self.user)
        self.api_client = TestApiClient()

        self.data = {'format': 'json', 'username': self.user.username, 'api_key': self.user.api_key.key}

    def get_credentials(self):
        credentials = self.create_apikey(username=self.user.username, api_key=self.user.api_key.key)
        return credentials

    def test_get_list_of_messages(self):
        url = '/api/v1/person/'
        response = self.api_client.get(url, authentication=self.get_credentials())

        self.assertValidJSONResponse(response)

        persons = self.deserialize(response)['objects']
        self.assertEqual(len(persons), Person.objects.count())  # All the instances

    def test_unauthorized_list_of_persons(self):
        url = '/api/v1/person/'
        response = self.api_client.get(url)

        self.assertHttpUnauthorized(response)

    def test_the_remote_url_of_the_person_points_to_its_popit_instance(self):
        url = '/api/v1/person/'
        response = self.api_client.get(url, authentication=self.get_credentials())
        persons = self.deserialize(response)['objects']
        self.assertEquals(persons[0]['popit_url'], persons[0]['resource_uri'])
