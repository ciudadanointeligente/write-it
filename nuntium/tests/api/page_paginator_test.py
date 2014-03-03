# -*- coding: utf-8 -*-
from django.core.management import call_command
from nuntium.models import Message, WriteItInstance, Confirmation
from tastypie.test import ResourceTestCase, TestApiClient
from django.contrib.auth.models import User
from nuntium.api import PagePaginator
from django.utils.unittest import skip
from tastypie.paginator import Paginator

class PagePaginationTestCase(ResourceTestCase):
    def setUp(self):
        super(PagePaginationTestCase,self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.user = User.objects.all()[0]
        # self.writeitinstance = WriteItInstance.objects.create(name="a test", slug="a-test", owner=self.user)
        self.api_client = TestApiClient()
        self.data = {'format': 'json', 'username': self.user.username, 'api_key':self.user.api_key.key}

    def test_setting_all_variables(self):
        request_data = {
        'limit':None,
        'offset':0
        }
        objects = Message.objects.all()
        paginator = PagePaginator(request_data, objects)
        self.assertIsInstance(paginator, Paginator)


    def test_get_offset(self):
    	request_data = {
        'limit':None,
        'offset':5
        }
        objects = Message.objects.all()
        paginator = PagePaginator(request_data, objects)
        self.assertEquals(paginator.get_offset(), request_data['offset'])

    def assertOffsetEquals(self, page, limit, offset, objects=Message.objects.all()):
    	request_data = {
    		'limit':limit,
    		'page': page
    	}
    	objects = objects
    	paginator = PagePaginator(request_data, objects)
    	self.assertEquals(paginator.get_offset(), offset)

    def test_get_page(self):
    	self.assertOffsetEquals(1, 1, 0)
    	self.assertOffsetEquals(1, 2, 0)
    	self.assertOffsetEquals(2, 1, 1)
    	self.assertOffsetEquals(2, 2, 2)

    def test_get_paginated(self):
    	url = '/api/v1/message/'
    	data = self.data
    	data['page'] = 2
    	data['limit'] = 1
        for message in Message.objects.all():
            Confirmation.objects.create(message=message)
            message.recently_confirmated()


        response = self.api_client.get(url,data = data)
        # All messages must be confirmed
        # in order to be in the api
        
        messages = self.deserialize(response)['objects']
        self.assertEquals(messages[0]['id'], Message.objects.public()[1].id)