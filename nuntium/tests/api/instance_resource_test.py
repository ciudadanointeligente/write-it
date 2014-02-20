# -*- coding: utf-8 -*-
from django.core.management import call_command
from nuntium.models import Message, WriteItInstance
from tastypie.test import ResourceTestCase, TestApiClient
from django.contrib.auth.models import User
from tastypie.models import ApiKey
from popit.models import Person
from global_test_case import GlobalTestCase as TestCase, popit_load_data
from django.utils.unittest import skip, skipUnless
from django.conf import settings
import re
from django.utils.encoding import force_text

class InstanceResourceTestCase(ResourceTestCase):
    def setUp(self):
        super(InstanceResourceTestCase,self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.user = User.objects.all()[0]
        self.writeitinstance = WriteItInstance.objects.create(name="a test", slug="a-test", owner=self.user)
        self.api_client = TestApiClient()
        self.data = {'format': 'json', 'username': self.user.username, 'api_key':self.user.api_key.key}

    def get_credentials(self):
        credentials = self.create_apikey(username=self.user.username, api_key=self.user.api_key.key)
        return credentials

    def test_api_exists(self):
        url = '/api/v1/'
        resp = self.api_client.get(url,data = self.data)
        
        self.assertValidJSONResponse(resp)

    def test_api_needs_authentication(self):
        url = '/api/v1/instance/'
        response = self.api_client.get(url)

        self.assertHttpUnauthorized(response)

    def test_get_list_of_instances(self):
        url = '/api/v1/instance/'
        response = self.api_client.get(url,data = self.data)


        self.assertValidJSONResponse(response)

        instances = self.deserialize(response)['objects']
        self.assertEqual(len(instances), WriteItInstance.objects.count()) #All the instances
        first_instance = instances[0]
        self.assertEqual(first_instance['messages_uri'],'/api/v1/instance/{0}/messages/'.format(first_instance['id']))


    def test_get_detail_of_an_instance(self):
        url = '/api/v1/instance/{0}/'.format(self.writeitinstance.id)
        response = self.api_client.get(url,data = self.data)

        self.assertValidJSONResponse(response)

    def test_get_persons_of_an_instance(self):
        writeitinstance = WriteItInstance.objects.all()[0]
        url = '/api/v1/instance/{0}/'.format(writeitinstance.id)
        response = self.api_client.get(url,data = self.data)
        instance = self.deserialize(response)
        self.assertIn('persons', instance)
        pedro = Person.objects.all()[0]
        self.assertIn(pedro.popit_url, instance['persons'])


    def test_get_list_of_messages_per_instance(self):
        
        pedro = Person.objects.all()[0]
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Fiera es una perra feroz', 
            writeitinstance= self.writeitinstance, 
            persons = [pedro])


        url = '/api/v1/instance/{0}/messages/'.format(self.writeitinstance.id)
        response = self.api_client.get(url,data = self.data)
        self.assertValidJSONResponse(response)
        messages = self.deserialize(response)['objects']
        

        self.assertEqual(len(messages), Message.objects.filter(writeitinstance=self.writeitinstance).count()) #All the instances
        self.assertEqual(messages[0]['id'], message.id)
        #assert that answers come in the

    def test_create_a_new_instance(self):
        instance_data = {
            'name' : 'The instance',
            'slug': 'the-instance'
        }
        url = '/api/v1/instance/'
        response = self.api_client.post(url, data = instance_data, format='json', authentication=self.get_credentials())
        self.assertHttpCreated(response)
        match_id = re.match(r'^http://testserver/api/v1/instance/(?P<id>\d+)/?', response['Location'])
        self.assertIsNotNone(match_id)
        instance_id = match_id.group('id')

        instance = WriteItInstance.objects.get(id=instance_id)
        self.assertValidJSON(force_text(response.content))
        instance_as_json = force_text(response.content)
        self.assertIn('resource_uri', instance_as_json)
        self.assertEquals(instance.name, instance_data['name'])
        self.assertEquals(instance.slug, instance_data['slug'])
        self.assertEquals(instance.owner, self.user)

    @skipUnless(settings.LOCAL_POPIT, "No local popit running")
    def test_create_a_new_instance_with_only_name(self):
        instance_data = {
            'name' : 'The instance'
        }
        url = '/api/v1/instance/'
        response = self.api_client.post(url, data = instance_data, format='json', authentication=self.get_credentials())
        self.assertHttpCreated(response)
        match_id = re.match(r'^http://testserver/api/v1/instance/(?P<id>\d+)/?', response['Location'])
        self.assertIsNotNone(match_id)
        instance_id = match_id.group('id')

        instance = WriteItInstance.objects.get(id=instance_id)


        self.assertEquals(instance.name, instance_data['name'])
        self.assertEquals(instance.owner, self.user)
        self.assertTrue(instance.slug)
    
    def test_does_not_create_a_user_if_not_logged(self):
        instance_data = {
            'name' : 'The instance',
            'slug': 'the-instance'
        }
        url = '/api/v1/instance/'
        response = self.api_client.post(url, data = instance_data, format='json')
        self.assertHttpUnauthorized(response)

    @skipUnless(settings.LOCAL_POPIT, "No local popit running")
    def test_create_and_pull_people_from_a_popit_api(self):
        #loading data into the popit-api
        popit_load_data()

        instance_data = {
            'name' : 'The instance',
            'slug': 'the-instance',
            'popit-api': settings.TEST_POPIT_API_URL
        }
        url = '/api/v1/instance/'
        response = self.api_client.post(url, data = instance_data, format='json', authentication=self.get_credentials())
        self.assertHttpCreated(response)
        match_id = re.match(r'^http://testserver/api/v1/instance/(?P<id>\d+)/?', response['Location'])

        instance = WriteItInstance.objects.get(id=match_id.group('id'))
        self.assertEquals(instance.persons.count(), 2)
        #this should not break
        raton = Person.objects.get(name='Ratón Inteligente')
        fiera = Person.objects.get(name="Fiera Feroz")

        self.assertIn(raton, [r for r in instance.persons.all()])
        self.assertIn(fiera, [r for r in instance.persons.all()])