# -*- coding: utf-8 -*-
from django.core.management import call_command
from ...models import Message, WriteItInstance
from tastypie.test import ResourceTestCase, TestApiClient
from django.contrib.auth.models import User
from tastypie.models import ApiKey
from popit.models import Person
from global_test_case import GlobalTestCase as TestCase, popit_load_data
from django.utils.unittest import skip
from django.conf import settings
import re
from django.utils.encoding import force_text
from ...api import AnswerResource
from django.http import HttpRequest
from ...models import Answer
from ...models import OutboundMessage, OutboundMessageIdentifier, Answer

class AnswerCreationResource(ResourceTestCase):
    def setUp(self):
        super(AnswerCreationResource, self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.outbound_message = OutboundMessage.objects.all()[0]
        self.identifier = OutboundMessageIdentifier.objects.get(outbound_message=self.outbound_message)
        self.api_client = TestApiClient()
        self.user = User.objects.all()[0]
        self.data = {'format': 'json', 'username': self.user.username, 'api_key':self.user.api_key.key}

    def get_credentials(self):
        credentials = self.create_apikey(username=self.user.username, api_key=self.user.api_key.key)
        return credentials


    def test_I_can_create_an_answer_with_only_an_identifier_and_a_content(self):
        url = '/api/v1/create_answer/'
        content = 'Fiera tiene una pulga'
        answer_data = {
        'key':self.identifier.key,
        'content':content
        }
        previous_answers = Answer.objects.count()
        response = self.api_client.post(url, data = answer_data, format='json', authentication=self.get_credentials())
        self.assertHttpCreated(response)

        answers_count = Answer.objects.count()

        self.assertEquals(answers_count, previous_answers + 1)


    def test_authorization_using_api_key(self):
        url = '/api/v1/create_answer/'
        content = 'una sola'
        answer_data = {
        'key':self.identifier.key,
        'content':content
        }
        response = self.api_client.post(url, data = answer_data, format='json')
        self.assertHttpUnauthorized(response)

    def test_only_the_owner_can_create_an_answer(self):
        not_the_owner = User.objects.create(username='not_the_owner')
        his_api_key = not_the_owner.api_key
        credentials = self.create_apikey(username=not_the_owner.username, api_key=his_api_key.key)
        url = '/api/v1/create_answer/'
        content = 'una sola'
        answer_data = {
        'key':self.identifier.key,
        'content':content
        }

        response = self.api_client.post(url, data = answer_data, format='json', authentication=credentials)
        self.assertHttpUnauthorized(response)


    def test_only_post_endpoint(self):
        url = '/api/v1/create_answer/'
        content = 'una sola'
        answer_data = {
            'key':self.identifier.key,
            'content':content
        }
        response = self.api_client.get(url)
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.put(url, data = answer_data)
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.patch(url, data = answer_data)
        self.assertHttpMethodNotAllowed(response)