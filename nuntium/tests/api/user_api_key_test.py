# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from global_test_case import GlobalTestCase as TestCase


class UserApiKeyTestCase(TestCase):
    def setUp(self):
        pass

    def test_automatic_creation_of_api_key_for_new_user(self):
        user = User.objects.create_user(username="new_user", password="password")
        self.assertIsNotNone(user.api_key)
        self.assertTrue(user.api_key.key)
