# -*- coding: utf-8 -*-
from django.core.management import call_command
from tastypie.test import ResourceTestCase, TestApiClient
from django.contrib.auth.models import User
from ...models import OutboundMessage, OutboundMessageIdentifier, Answer


class AnswerCreationResource(ResourceTestCase):
    def setUp(self):
        super(AnswerCreationResource, self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.outbound_message = OutboundMessage.objects.get(id=1)
        self.identifier = OutboundMessageIdentifier.objects.get(outbound_message=self.outbound_message)
        self.api_client = TestApiClient()
        self.user = User.objects.get(id=1)
        self.data = {'format': 'json', 'username': self.user.username, 'api_key': self.user.api_key.key}

    def get_credentials(self):
        credentials = self.create_apikey(username=self.user.username, api_key=self.user.api_key.key)
        return credentials

    def test_I_can_create_an_answer_with_only_an_identifier_and_a_content(self):
        url = '/api/v1/create_answer/'
        content = 'Fiera tiene una pulga'
        answer_data = {
            'key': self.identifier.key,
            'content': content,
            }
        previous_answers = Answer.objects.count()
        response = self.api_client.post(url,
            data=answer_data,
            format='json',
            authentication=self.get_credentials(),)
        self.assertHttpCreated(response)

        answers_count = Answer.objects.count()

        self.assertEquals(answers_count, previous_answers + 1)
        answer_json = self.deserialize(response)
        self.assertEquals(answer_json['content'], content)
        self.assertIn('id', answer_json.keys())

    def test_authorization_using_api_key(self):
        url = '/api/v1/create_answer/'
        content = 'una sola'
        answer_data = {
            'key': self.identifier.key,
            'content': content,
            }
        response = self.api_client.post(url, data=answer_data, format='json')
        self.assertHttpUnauthorized(response)

    def test_only_the_owner_can_create_an_answer(self):
        not_the_owner = User.objects.create(username='not_the_owner')
        his_api_key = not_the_owner.api_key
        credentials = self.create_apikey(username=not_the_owner.username, api_key=his_api_key.key)
        url = '/api/v1/create_answer/'
        content = 'una sola'
        answer_data = {
            'key': self.identifier.key,
            'content': content,
            }

        response = self.api_client.post(url, data=answer_data, format='json', authentication=credentials)
        self.assertHttpUnauthorized(response)

    def test_only_post_endpoint(self):
        url = '/api/v1/create_answer/'
        content = 'una sola'
        answer_data = {
            'key': self.identifier.key,
            'content': content,
            }
        response = self.api_client.get(url)
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.put(url, data=answer_data)
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.patch(url, data=answer_data)
        self.assertHttpMethodNotAllowed(response)

    def test_if_configured_read_only_cannot_create(self):
        self.identifier.outbound_message.message.writeitinstance.config.api_read_only = True
        self.identifier.outbound_message.message.writeitinstance.config.save()
        url = '/api/v1/create_answer/'
        content = 'Fiera tiene una pulga'
        answer_data = {
            'key': self.identifier.key,
            'content': content,
            }
        response = self.api_client.post(url, data=answer_data, format='json', authentication=self.get_credentials())
        self.assertHttpUnauthorized(response)
