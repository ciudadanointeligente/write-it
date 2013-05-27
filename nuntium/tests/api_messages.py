# -*- coding: utf-8 -*-
from django.core.management import call_command
from nuntium.models import Message, WriteItInstance
from tastypie.test import ResourceTestCase, TestApiClient
from django.contrib.auth.models import User
from tastypie.models import ApiKey
from django.utils.unittest import skip

class InstanceResourceTestCase(ResourceTestCase):
    def setUp(self):
        super(InstanceResourceTestCase,self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.writeitinstance = WriteItInstance.objects.create(name="a test", slug="a-test")
        self.api_client = TestApiClient()
        self.user = User.objects.create_user(username='the_user',
                                                password='joe',
                                                email='doe@joe.cl')
        ApiKey.objects.create(user=self.user)

        self.data = {'format': 'json', 'username': self.user.username, 'api_key':self.user.api_key.key}


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


    def test_get_detail_of_an_instance(self):
        url = '/api/v1/instance/{0}/'.format(self.writeitinstance.id)
        response = self.api_client.get(url,data = self.data)

        self.assertValidJSONResponse(response)

    #@skip("need the message Resource")
    def test_get_list_of_messages_per_instance(self):
        url = '/api/v1/instance/{0}/messages/'.format(self.writeitinstance.id)
        response = self.api_client.get(url,data = self.data)

        self.assertValidJSONResponse(response)

        messages = self.deserialize(response)['objects']

        self.assertEqual(len(messages), Message.objects.filter(writeitinstance=self.writeitinstance).count()) #All the instances



class MessageResourceTestCase(ResourceTestCase):
    def setUp(self):
        super(MessageResourceTestCase,self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.writeitinstance = WriteItInstance.objects.create(name="a test", slug="a-test")
        self.api_client = TestApiClient()
        self.user = User.objects.create_user(username='the_user',
                                                password='joe',
                                                email='doe@joe.cl')
        ApiKey.objects.create(user=self.user)

        self.data = {'format': 'json', 'username': self.user.username, 'api_key':self.user.api_key.key}

    def test_get_list_of_messages(self):
        url = '/api/v1/message/'
        response = self.api_client.get(url,data = self.data)


        self.assertValidJSONResponse(response)

        instances = self.deserialize(response)['objects']
        self.assertEqual(len(instances), Message.objects.count()) #All the instances


    def test_authentication(self):
        url = '/api/v1/message/'
        response = self.api_client.get(url)


        self.assertHttpUnauthorized(response)
