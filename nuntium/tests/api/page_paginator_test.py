# -*- coding: utf-8 -*-
from django.core.management import call_command
from nuntium.models import Message, WriteItInstance
from tastypie.test import ResourceTestCase, TestApiClient
from django.contrib.auth.models import User
from nuntium.api import PagePaginator
from tastypie.paginator import Paginator

class PagePaginationTestCase(ResourceTestCase):
    def setUp(self):
        super(PagePaginationTestCase,self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.user = User.objects.all()[0]
        self.writeitinstance = WriteItInstance.objects.create(name="a test", slug="a-test", owner=self.user)
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
