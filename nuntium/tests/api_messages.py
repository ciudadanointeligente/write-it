# -*- coding: utf-8 -*-
from django.core.management import call_command
from nuntium.models import Message, WriteItInstance
from tastypie.test import ResourceTestCase, TestApiClient

class MessageResourceTestCase(ResourceTestCase):
    def setUp(self):
        super(MessageResourceTestCase,self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.writeitinstance = WriteItInstance.objects.create()
        self.api_client = TestApiClient()


    def test_api_message_exists(self):
        url = '/api/v1/'
        resp = self.api_client.get(url)
        
        self.assertValidJSONResponse(resp)

