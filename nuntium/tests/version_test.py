# -*- coding: utf-8 -*-
import json
from global_test_case import GlobalTestCase as TestCase
from subdomains.utils import reverse
from django.core.management import call_command
from instance.models import PopoloPerson, WriteItInstance
from django.contrib.auth.models import User
from django.utils.encoding import force_text


class VersionTestCase(TestCase):
    def setUp(self):
        super(VersionTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.get(id=1)
        # call_command('loaddata', 'example_data', verbosity=0)

    def test_check_version_output(self):
        url = reverse("version")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertTrue(data.has_key('git_version'))
        self.assertFalse(data.has_key('message_count'))

    def test_check_instance_version_output(self):
        url = reverse('instance_version',
                subdomain=self.writeitinstance.slug)

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertTrue(data.has_key('git_version'))
        self.assertTrue(data.has_key('message_count'))

        self.assertEquals(data['message_count'], 1)
        self.assertEquals(data['answer_count'], 1)
        self.assertEquals(data['all_transactions'], 2)
