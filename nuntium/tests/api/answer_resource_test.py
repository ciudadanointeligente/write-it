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
from nuntium.api import AnswerResource
from django.http import HttpRequest
from nuntium.models import Answer

class AnswersResourceTestCase(ResourceTestCase):
    def setUp(self):
        super(AnswersResourceTestCase,self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.answer = Answer.objects.all()[0]
        self.writeitinstance = WriteItInstance.objects.all()[0]
        self.user = User.objects.all()[0]
        self.api_client = TestApiClient()
        self.data = {'format': 'json', 'username': self.user.username, 'api_key':self.user.api_key.key}


    def test_resource_get_all_answers(self):
        resource = AnswerResource()
        self.assertTrue(resource)

        request = HttpRequest()
        answers_json = self.deserialize(resource.get_list(request))['objects']
        self.assertEquals(len(answers_json), Answer.objects.count())
        self.assertEquals(answers_json[0]["id"], self.answer.id)

    def test_get_the_list_of_answers_per_instance(self):
        """Get the list of answers in an instance"""
        url = '/api/v1/instance/%(writeitinstance_id)i/answers/' % {
            'writeitinstance_id' : self.writeitinstance.id
        }
        response = self.api_client.get(url,data = self.data)
        self.assertValidJSONResponse(response)
        answers = self.deserialize(response)['objects']
        answers_of_the_writeitinstance = Answer.objects.filter(
            message__writeitinstance=self.writeitinstance
            )
        self.assertEquals(len(answers), len(answers_of_the_writeitinstance))
        self.assertEquals(answers[0]['content'], self.answer.content)
        self.assertEquals(answers[0]['id'], self.answer.id)


