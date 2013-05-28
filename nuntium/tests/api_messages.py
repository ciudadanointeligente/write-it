# -*- coding: utf-8 -*-
from django.core.management import call_command
from nuntium.models import Message, WriteItInstance
from tastypie.test import ResourceTestCase, TestApiClient
from django.contrib.auth.models import User
from tastypie.models import ApiKey
from django.utils.unittest import skip
from popit.models import Person

class InstanceResourceTestCase(ResourceTestCase):
    def setUp(self):
        super(InstanceResourceTestCase,self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.writeitinstance = WriteItInstance.objects.create(name="a test", slug="a-test")
        self.api_client = TestApiClient()
        self.user = User.objects.create_user(username='the_user',
                                                password='joe',
                                                email='doe@joe.cl')
        ApiKey.objects.create(user=self.user)

        self.data = {'format': 'json', 'username': self.user.username, 'api_key':self.user.api_key.key}



    def test_api_exists(self):
        url = '/api/v1/'
        resp = self.api_client.get(url,data = self.data)
        
        self.assertValidJSONResponse(resp)

    def test_api_needs_authentication(self):
        url = '/api/v1/instance/'
        response = self.api_client.get(url)

        self.assertHttpUnauthorized(response)

    def test_get_list_of_instances(self):
        url = '/api/v1/instance/'
        response = self.api_client.get(url,data = self.data)


        self.assertValidJSONResponse(response)

        instances = self.deserialize(response)['objects']
        self.assertEqual(len(instances), WriteItInstance.objects.count()) #All the instances


    def test_get_detail_of_an_instance(self):
        url = '/api/v1/instance/{0}/'.format(self.writeitinstance.id)
        response = self.api_client.get(url,data = self.data)

        self.assertValidJSONResponse(response)

    def test_get_list_of_messages_per_instance(self):
        
        pedro = Person.objects.all()[0]
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Fiera es una perra feroz', 
            writeitinstance= self.writeitinstance, 
            persons = [pedro])


        url = '/api/v1/instance/{0}/messages/'.format(self.writeitinstance.id)
        response = self.api_client.get(url,data = self.data)
        self.assertValidJSONResponse(response)
        messages = self.deserialize(response)['objects']
        

        self.assertEqual(len(messages), Message.objects.filter(writeitinstance=self.writeitinstance).count()) #All the instances
        self.assertEqual(messages[0]['id'], message.id)
        #assert that answers come in the 



class MessageResourceTestCase(ResourceTestCase):
    def setUp(self):
        super(MessageResourceTestCase,self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.writeitinstance = WriteItInstance.objects.create(name="a test", slug="a-test")

        self.api_client = TestApiClient()
        self.user = User.objects.create_user(username='the_user',
                                                password='joe',
                                                email='doe@joe.cl'
                                                )
        self.user.is_staff = True
        self.user.save()
        ApiKey.objects.create(user=self.user)

        self.data = {'format': 'json', 'username': self.user.username, 'api_key':self.user.api_key.key}

    def test_get_list_of_messages(self):
        url = '/api/v1/message/'
        response = self.api_client.get(url,data = self.data)


        self.assertValidJSONResponse(response)

        messages = self.deserialize(response)['objects']
        self.assertEqual(len(messages), Message.objects.count()) #All the instances


    def test_authentication(self):
        url = '/api/v1/message/'
        response = self.api_client.get(url)


        self.assertHttpUnauthorized(response)

    def test_a_list_of_messages_have_answers(self):
        url = '/api/v1/message/'
        response = self.api_client.get(url,data = self.data)
        self.assertValidJSONResponse(response)
        messages = self.deserialize(response)['objects']

        self.assertTrue('answers' in messages[0])

    def get_credentials(self):
        credentials = self.create_apikey(username=self.user.username, api_key=self.user.api_key.key)
        return credentials

    def test_create_a_new_message(self):
        writeitinstance = WriteItInstance.objects.all()[0]
        message_data = {
            'author_name' : 'Felipipoo',
            'subject': 'new message',
            'content': 'the content thing',
            'writeitinstance': '/api/v1/instance/{0}/'.format(writeitinstance.id),
            'persons': [writeitinstance.persons.all()[0].pk]
        }

        url = '/api/v1/message/'
        previous_amount_of_messages = Message.objects.count()
        response = self.api_client.post(url, data = message_data, format='json', authentication=self.get_credentials())
        self.assertHttpCreated(response)

        post_amount_of_messages = Message.objects.count()
        self.assertEquals(post_amount_of_messages, previous_amount_of_messages + 1)




from nuntium.api import AnswerResource
from django.http import HttpRequest
from nuntium.models import Answer
class AnswersResourceTestCase(ResourceTestCase):
    def setUp(self):
        super(AnswersResourceTestCase,self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.answer = Answer.objects.create(message=Message.objects.all()[0], person=Person.objects.all()[0])


    def test_resource_get_all_answers(self):
        resource = AnswerResource()

        self.assertTrue(resource)

        request = HttpRequest()
        answers_json = self.deserialize(resource.get_list(request))['objects']
        self.assertEquals(len(answers_json), Answer.objects.count())
        self.assertEquals(answers_json[0]["id"], self.answer.id)

