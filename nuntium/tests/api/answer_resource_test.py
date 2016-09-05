# -*- coding: utf-8 -*-
from django.core.management import call_command
from instance.models import WriteItInstance
from tastypie.test import ResourceTestCase, TestApiClient
from django.contrib.auth.models import User
from popolo.models import Person
from ...api import AnswerResource
from django.http import HttpRequest
from ...models import Answer, Message


class AnswersResourceTestCase(ResourceTestCase):
    def setUp(self):
        super(AnswersResourceTestCase, self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.writeitinstance = WriteItInstance.objects.get(id=1)
        self.user = User.objects.get(id=1)
        self.api_client = TestApiClient()
        self.data = {'format': 'json', 'username': self.user.username, 'api_key': self.user.api_key.key}

    def test_resource_get_all_answers(self):
        '''Get all answers through the API'''
        resource = AnswerResource()
        self.assertTrue(resource)

        request = HttpRequest()
        answers_json = self.deserialize(resource.get_list(request))['objects']
        self.assertEquals(
            set([x.id for x in Answer.objects.all()]),
            set([x['id'] for x in answers_json])
            )

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

        self.assertEquals(
            set([(x.id, x.content, x.message_id) for x in answers_of_the_writeitinstance]),
            set([(x['id'], x['content'], x['message_id']) for x in answers])
            )

    def test_get_only_answers_of_the_instance(self):
        """Show answers from the writeitinstance only"""
        the_other_instance = WriteItInstance.objects.get(id=2)
        person = Person.objects.get(id=1)
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

        db_answer = Answer.objects.get(pk=answer_json.get('id'))

        self.assertEquals(person["id"], db_answer.person.id)
        self.assertEquals(person["image"], db_answer.person.image)
        self.assertEquals(person["name"], db_answer.person.name)
        self.assertEquals(person["popit_id"], db_answer.person.popit_id)
        self.assertEquals(person["popit_url"], db_answer.person.popit_url)
        self.assertEquals(person["resource_uri"], db_answer.person.popit_url)
        self.assertEquals(person["summary"], db_answer.person.summary)

    def test_answer_ordering(self):
        """The answers are displayed from new to old"""
        person = Person.objects.get(id=1)
        message = Message.objects.get(id=1)

        Answer.objects.all().delete()
        answer2 = Answer.objects.create(
            message=message,
            content="hello this is an answer",
            person=person,
            )
        answer1 = Answer.objects.create(
            message=message,
            content="hello this is an answer",
            person=person,
            )
        answers_json = self.deserialize(AnswerResource().get_list(HttpRequest()))['objects']
        self.assertEquals(answers_json[0]['id'], answer1.id)
        self.assertEquals(answers_json[1]['id'], answer2.id)
