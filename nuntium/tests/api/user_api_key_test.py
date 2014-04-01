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

class UserApiKeyTestCase(TestCase):
    def setUp(self):
        pass

    def test_automatic_creation_of_api_key_for_new_user(self):
        user = User.objects.create_user(username="new_user", password="password")
        self.assertIsNotNone(user.api_key)
        self.assertTrue(user.api_key.key)