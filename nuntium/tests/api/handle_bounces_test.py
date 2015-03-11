# -*- coding: utf-8 -*-
from django.core.management import call_command
from tastypie.test import ResourceTestCase, TestApiClient
from django.contrib.auth.models import User
from ...models import OutboundMessage, OutboundMessageIdentifier


class HandleBounces(ResourceTestCase):
    def setUp(self):
        super(HandleBounces, self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.api_client = TestApiClient()
        self.user = User.objects.get(id=1)
        self.outbound_message = OutboundMessage.objects.get(id=1)
        self.identifier = OutboundMessageIdentifier.objects.get(outbound_message=self.outbound_message)

    def get_credentials(self):
        credentials = self.create_apikey(username=self.user.username, api_key=self.user.api_key.key)
        return credentials

    def test_handle_bounces_endpoint(self):
        url = '/api/v1/handle_bounce/'
        bounce_data = {
            'key': self.identifier.key,
        }
        resp = self.api_client.post(url, data=bounce_data, authentication=self.get_credentials())
        self.assertHttpCreated(resp)

    def test_handle_bounces_sets_the_contact_to_bounced(self):
        url = '/api/v1/handle_bounce/'
        bounce_data = {
            'key': self.identifier.key,
            }
        self.api_client.post(url, data=bounce_data, authentication=self.get_credentials())

        self.assertTrue(self.outbound_message.contact.is_bounced)
