# -*- coding: utf-8 -*-
from django.core.management import call_command
from ...models import WriteItInstance
from tastypie.test import ResourceTestCase, TestApiClient
from django.contrib.auth.models import User
from popit.models import Person
from ...api import AnswerResource
from django.http import HttpRequest
from ...models import Answer


class AnswersResourceTestCase(ResourceTestCase):
    def setUp(self):
        super(AnswersResourceTestCase, self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.answer = Answer.objects.all()[0]
        self.writeitinstance = WriteItInstance.objects.all()[0]
        self.user = User.objects.all()[0]
        self.api_client = TestApiClient()
        self.data = {'format': 'json', 'username': self.user.username, 'api_key': self.user.api_key.key}

    def test_resource_get_all_answers(self):
        '''Get all answers through the API'''
        resource = AnswerResource()
        self.assertTrue(resource)

        request = HttpRequest()
        answers_json = self.deserialize(resource.get_list(request))['objects']
        self.assertEquals(len(answers_json), Answer.objects.count())
        self.assertEquals(answers_json[0]["id"], self.answer.id)

    def test_get_the_list_of_answers_per_instance(self):
        """Get the list of answers in an writetinstance instance"""
        url = '/api/v1/instance/%(writeitinstance_id)i/answers/' % {
            'writeitinstance_id': self.writeitinstance.id,
        }
        response = self.api_client.get(url, data=self.data)
        self.assertValidJSONResponse(response)
        answers = self.deserialize(response)['objects']
        answers_of_the_writeitinstance = Answer.objects.filter(
            message__writeitinstance=self.writeitinstance
            )
        self.assertEquals(len(answers), len(answers_of_the_writeitinstance))
        self.assertEquals(answers[0]['content'], self.answer.content)
        self.assertEquals(answers[0]['id'], self.answer.id)
        self.assertEquals(answers[0]['message_id'], self.answer.message.id)

    def test_get_only_answers_of_the_instance(self):
        """Show answers from the writeitinstance only"""
        the_other_instance = WriteItInstance.objects.all()[1]
        person = Person.objects.all()[0]
        message = the_other_instance.message_set.all()[0]
        answer = Answer.objects.create(
            message=message,
            content="hello this is an answer",
            person=person,
            )

        url = '/api/v1/instance/%(writeitinstance_id)i/answers/' % {
            'writeitinstance_id': the_other_instance.id,
        }
        response = self.api_client.get(url, data=self.data)
        answers = self.deserialize(response)['objects']
        answers_of_the_other_instance = Answer.objects.filter(
            message__writeitinstance=the_other_instance
            )
        self.assertEquals(len(answers), len(answers_of_the_other_instance))
        self.assertEquals(answers[0]['id'], answer.id)
        self.assertEquals(answers[0]['content'], answer.content)

    def test_get_the_person_that_answered(self):
        '''The API tells who answered the current answer'''
        resource = AnswerResource()

        request = HttpRequest()
        answers_json = self.deserialize(resource.get_list(request))['objects']
        answer_json = answers_json[0]

        self.assertIn('person', answer_json)
        person = answer_json['person']

        self.assertEquals(person["id"], self.answer.person.id)
        self.assertEquals(person["image"], self.answer.person.image)
        self.assertEquals(person["name"], self.answer.person.name)
        self.assertEquals(person["popit_id"], self.answer.person.popit_id)
        self.assertEquals(person["popit_url"], self.answer.person.popit_url)
        self.assertEquals(person["resource_uri"], self.answer.person.popit_url)
        self.assertEquals(person["summary"], self.answer.person.summary)

    def test_answer_ordering(self):
        """The answers are displayed from new to old"""
        Answer.objects.all().delete()
        answer2 = Answer.objects.create(
            message=self.answer.message,
            content="hello this is an answer",
            person=self.answer.person,
            )
        answer1 = Answer.objects.create(
            message=self.answer.message,
            content="hello this is an answer",
            person=self.answer.person,
            )
        answers_json = self.deserialize(AnswerResource().get_list(HttpRequest()))['objects']
        for answer in answers_json:
            print answer['id'], answer['created']
        self.assertEquals(answers_json[0]['id'], answer1.id)
        self.assertEquals(answers_json[1]['id'], answer2.id)
