# -*- coding: utf-8 -*-
from django.core.management import call_command
from nuntium.models import Message, WriteItInstance
from tastypie.test import ResourceTestCase, TestApiClient
from django.contrib.auth.models import User
from tastypie.models import ApiKey
from popit.models import Person
from global_test_case import GlobalTestCase as TestCase, popit_load_data
from django.utils.unittest import skip
from django.conf import settings
import re
from django.utils.encoding import force_text

class MessageResourceTestCase(ResourceTestCase):
    def setUp(self):
        super(MessageResourceTestCase,self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.user = User.objects.all()[0]
        self.writeitinstance = WriteItInstance.objects.create(name="a test", slug="a-test", owner=self.user)
        self.api_client = TestApiClient()
        self.data = {'format': 'json', 'username': self.user.username, 'api_key':self.user.api_key.key}

    def get_credentials(self):
        credentials = self.create_apikey(username=self.user.username, api_key=self.user.api_key.key)
        return credentials

    def test_get_list_of_messages(self):
        url = '/api/v1/message/'
        response = self.api_client.get(url,data = self.data)


        self.assertValidJSONResponse(response)

        messages = self.deserialize(response)['objects']
        self.assertEqual(len(messages), Message.objects.count()) #All the instances


    def test_authentication(self):
        url = '/api/v1/message/'
        response = self.api_client.get(url)

        self.assertHttpUnauthorized(response)

    def test_a_list_of_messages_have_answers(self):
        url = '/api/v1/message/'
        response = self.api_client.get(url,data = self.data)
        self.assertValidJSONResponse(response)
        messages = self.deserialize(response)['objects']

        self.assertTrue('answers' in messages[0])

    def test_the_message_has_the_people_it_was_sent_to(self):
        url = '/api/v1/message/'
        response = self.api_client.get(url,data = self.data)
        self.assertValidJSONResponse(response)
        messages = self.deserialize(response)['objects']

        self.assertTrue('persons' in messages[0])
        message = Message.objects.get(id=messages[0]['id'])
        for person in message.people:
            self.assertIn(person.popit_url, messages[0]['persons'])



    def test_create_a_new_message(self):
        writeitinstance = WriteItInstance.objects.all()[0]
        message_data = {
            'author_name' : 'Felipipoo',
            'subject': 'new message',
            'content': 'the content thing',
            'writeitinstance': '/api/v1/instance/{0}/'.format(writeitinstance.id),
            'persons': [writeitinstance.persons.all()[0].popit_url]
        }

        url = '/api/v1/message/'
        previous_amount_of_messages = Message.objects.count()
        response = self.api_client.post(url, data = message_data, format='json', authentication=self.get_credentials())
        self.assertHttpCreated(response)
        self.assertValidJSON(force_text(response.content))
        message_as_json = force_text(response.content)
        self.assertIn('resource_uri', message_as_json)

        post_amount_of_messages = Message.objects.count()
        self.assertEquals(post_amount_of_messages, previous_amount_of_messages + 1)


        the_message = Message.objects.get(author_name='Felipipoo')

        outbound_messages = the_message.outboundmessage_set.all()
        self.assertTrue(outbound_messages.count() > 0)
        for outbound_message in outbound_messages:
            self.assertEquals(outbound_message.status, 'ready')

    def test_create_a_new_message_with_a_non_existing_person(self):
        writeitinstance = WriteItInstance.objects.all()[0]
        message_data = {
            'author_name' : 'Felipipoo',
            'subject': 'new message',
            'content': 'the content thing',
            'writeitinstance': '/api/v1/instance/{0}/'.format(writeitinstance.id),
            'persons': [
            writeitinstance.persons.all()[0].popit_url,
            'http://this.person.does.not.exist'
            ]
        }
        url = '/api/v1/message/'
        previous_amount_of_messages = Message.objects.count()
        response = self.api_client.post(url, data = message_data, format='json', authentication=self.get_credentials())
        self.assertHttpCreated(response)
        the_message = Message.objects.get(author_name='Felipipoo')
        outbound_messages = the_message.outboundmessage_set.all()
        self.assertEquals(outbound_messages.count(), 1)
        self.assertEquals(outbound_messages[0].contact.person,writeitinstance.persons.all()[0] )

    def test_create_a_new_message_confirmated(self):
        writeitinstance = WriteItInstance.objects.all()[0]
        message_data = {
            'author_name' : 'Felipipoo',
            'subject': 'new message',
            'content': 'the content thing',
            'writeitinstance': '/api/v1/instance/{0}/'.format(writeitinstance.id),
            'persons': [writeitinstance.persons.all()[0].popit_url]
        }
        url = '/api/v1/message/'
        response = self.api_client.post(url, data = message_data, format='json', authentication=self.get_credentials())

        the_message = Message.objects.get(author_name='Felipipoo')

        self.assertTrue(the_message.confirmated)

    def test_create_a_new_message_to_all_persons_in_the_instance(self):
        #here it is the thing I don't know yet how to do this and I'll go for 
        #saying all in the persons array instead of having an array or an empty
        writeitinstance = WriteItInstance.objects.all()[0]
        message_data = {
            'author_name' : 'Felipipoo',
            'subject': 'new message',
            'content': 'the content thing',
            'writeitinstance': '/api/v1/instance/{0}/'.format(writeitinstance.id),
            'persons': "all"
        }
        url = '/api/v1/message/'
        response = self.api_client.post(url, data = message_data, format='json', authentication=self.get_credentials())
        
        the_message = Message.objects.get(author_name='Felipipoo')

        self.assertEquals(len(the_message.people), writeitinstance.persons.count())
        self.assertQuerysetEqual(the_message.people.all(), \
            [repr(r) for r in writeitinstance.persons.all()]
            )