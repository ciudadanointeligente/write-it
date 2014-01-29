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

class UserApiKeyTestCase(TestCase):
    def setUp(self):
        pass

    def test_automatic_creation_of_api_key_for_new_user(self):
        user = User.objects.create_user(username="new_user", password="password")
        self.assertIsNotNone(user.api_key)
        self.assertTrue(user.api_key.key)


class InstanceResourceTestCase(ResourceTestCase):
    def setUp(self):
        super(InstanceResourceTestCase,self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.user = User.objects.all()[0]
        self.writeitinstance = WriteItInstance.objects.create(name="a test", slug="a-test", owner=self.user)
        self.api_client = TestApiClient()
        self.data = {'format': 'json', 'username': self.user.username, 'api_key':self.user.api_key.key}

    def get_credentials(self):
        credentials = self.create_apikey(username=self.user.username, api_key=self.user.api_key.key)
        return credentials

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
        first_instance = instances[0]
        self.assertEqual(first_instance['messages_uri'],'/api/v1/instance/{0}/messages/'.format(first_instance['id']))


    def test_get_detail_of_an_instance(self):
        url = '/api/v1/instance/{0}/'.format(self.writeitinstance.id)
        response = self.api_client.get(url,data = self.data)

        self.assertValidJSONResponse(response)

    def test_get_persons_of_an_instance(self):
        writeitinstance = WriteItInstance.objects.all()[0]
        url = '/api/v1/instance/{0}/'.format(writeitinstance.id)
        response = self.api_client.get(url,data = self.data)
        instance = self.deserialize(response)
        self.assertIn('persons', instance)
        pedro = Person.objects.all()[0]
        self.assertIn(pedro.popit_url, instance['persons'])


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

    def test_create_a_new_instance(self):
        instance_data = {
            'name' : 'The instance',
            'slug': 'the-instance'
        }
        url = '/api/v1/instance/'
        response = self.api_client.post(url, data = instance_data, format='json', authentication=self.get_credentials())
        self.assertHttpCreated(response)
        match_id = re.match(r'^http://testserver/api/v1/instance/(?P<id>\d+)/?', response['Location'])
        self.assertIsNotNone(match_id)
        instance_id = match_id.group('id')

        instance = WriteItInstance.objects.get(id=instance_id)
        self.assertValidJSON(force_text(response.content))
        instance_as_json = force_text(response.content)
        self.assertIn('resource_uri', instance_as_json)
        self.assertEquals(instance.name, instance_data['name'])
        self.assertEquals(instance.slug, instance_data['slug'])
        self.assertEquals(instance.owner, self.user)

    def test_create_a_new_instance_with_only_name(self):
        instance_data = {
            'name' : 'The instance'
        }
        url = '/api/v1/instance/'
        response = self.api_client.post(url, data = instance_data, format='json', authentication=self.get_credentials())
        self.assertHttpCreated(response)
        match_id = re.match(r'^http://testserver/api/v1/instance/(?P<id>\d+)/?', response['Location'])
        self.assertIsNotNone(match_id)
        instance_id = match_id.group('id')

        instance = WriteItInstance.objects.get(id=instance_id)


        self.assertEquals(instance.name, instance_data['name'])
        self.assertEquals(instance.owner, self.user)
        self.assertTrue(instance.slug)
    
    def test_does_not_create_a_user_if_not_logged(self):
        instance_data = {
            'name' : 'The instance',
            'slug': 'the-instance'
        }
        url = '/api/v1/instance/'
        response = self.api_client.post(url, data = instance_data, format='json')
        self.assertHttpUnauthorized(response)

    def test_create_and_pull_people_from_a_popit_api(self):
        #loading data into the popit-api
        popit_load_data()

        instance_data = {
            'name' : 'The instance',
            'slug': 'the-instance',
            'popit-api': settings.TEST_POPIT_API_URL
        }
        url = '/api/v1/instance/'
        response = self.api_client.post(url, data = instance_data, format='json', authentication=self.get_credentials())
        self.assertHttpCreated(response)
        match_id = re.match(r'^http://testserver/api/v1/instance/(?P<id>\d+)/?', response['Location'])

        instance = WriteItInstance.objects.get(id=match_id.group('id'))
        self.assertEquals(instance.persons.count(), 2)
        #this should not break
        raton = Person.objects.get(name='Ratón Inteligente')
        fiera = Person.objects.get(name="Fiera Feroz")

        self.assertIn(raton, [r for r in instance.persons.all()])
        self.assertIn(fiera, [r for r in instance.persons.all()])




class PersonResourceTestCase(ResourceTestCase):
    def setUp(self):
        super(PersonResourceTestCase, self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.user = User.objects.all()[0]
        self.writeitinstance = WriteItInstance.objects.create(name="a test", slug="a-test", owner=self.user)
        self.api_client = TestApiClient()

        self.data = {'format': 'json', 'username': self.user.username, 'api_key':self.user.api_key.key}


    def get_credentials(self):
        credentials = self.create_apikey(username=self.user.username, api_key=self.user.api_key.key)
        return credentials


    def test_get_list_of_messages(self):
        url = '/api/v1/person/'
        response = self.api_client.get(url, authentication=self.get_credentials())


        self.assertValidJSONResponse(response)

        persons = self.deserialize(response)['objects']
        self.assertEqual(len(persons), Person.objects.count()) #All the instances


    def test_unauthorized_list_of_persons(self):
        url = '/api/v1/person/'
        response = self.api_client.get(url)

        self.assertHttpUnauthorized(response)


    def test_the_remote_url_of_the_person_points_to_its_popit_instance(self):
        url = '/api/v1/person/'
        response = self.api_client.get(url, authentication=self.get_credentials())
        persons = self.deserialize(response)['objects']
        self.assertEquals(persons[0]['popit_url'], persons[0]['resource_uri'])






class MessageResourceTestCase(ResourceTestCase):
    def setUp(self):
        super(MessageResourceTestCase,self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.user = User.objects.all()[0]
        self.writeitinstance = WriteItInstance.objects.create(name="a test", slug="a-test", owner=self.user)
        self.api_client = TestApiClient()
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
            'persons': [writeitinstance.persons.all()[0].popit_url]
        }

        url = '/api/v1/message/'
        previous_amount_of_messages = Message.objects.count()
        response = self.api_client.post(url, data = message_data, format='json', authentication=self.get_credentials())
        self.assertHttpCreated(response)
        self.assertValidJSON(force_text(response.content))
        message_as_json = force_text(response.content)
        self.assertIn('resource_uri', message_as_json)

        post_amount_of_messages = Message.objects.count()
        self.assertEquals(post_amount_of_messages, previous_amount_of_messages + 1)


        the_message = Message.objects.get(author_name='Felipipoo')

        outbound_messages = the_message.outboundmessage_set.all()
        self.assertTrue(outbound_messages.count() > 0)
        for outbound_message in outbound_messages:
            self.assertEquals(outbound_message.status, 'ready')

    def test_create_a_new_message_with_a_non_existing_person(self):
        writeitinstance = WriteItInstance.objects.all()[0]
        message_data = {
            'author_name' : 'Felipipoo',
            'subject': 'new message',
            'content': 'the content thing',
            'writeitinstance': '/api/v1/instance/{0}/'.format(writeitinstance.id),
            'persons': [
            writeitinstance.persons.all()[0].popit_url,
            'http://this.person.does.not.exist'
            ]
        }


        url = '/api/v1/message/'
        previous_amount_of_messages = Message.objects.count()
        response = self.api_client.post(url, data = message_data, format='json', authentication=self.get_credentials())
        self.assertHttpCreated(response)
        the_message = Message.objects.get(author_name='Felipipoo')
        outbound_messages = the_message.outboundmessage_set.all()
        self.assertEquals(outbound_messages.count(), 1)
        self.assertEquals(outbound_messages[0].contact.person,writeitinstance.persons.all()[0] )

    def test_create_a_new_message_confirmated(self):
        writeitinstance = WriteItInstance.objects.all()[0]
        message_data = {
            'author_name' : 'Felipipoo',
            'subject': 'new message',
            'content': 'the content thing',
            'writeitinstance': '/api/v1/instance/{0}/'.format(writeitinstance.id),
            'persons': [writeitinstance.persons.all()[0].popit_url]
        }
        url = '/api/v1/message/'
        response = self.api_client.post(url, data = message_data, format='json', authentication=self.get_credentials())

        the_message = Message.objects.get(author_name='Felipipoo')

        self.assertTrue(the_message.confirmated)


    def test_create_a_new_message_to_all_persons_in_the_instance(self):
        #here it is the thing I don't know yet how to do this and I'll go for 
        #saying all in the persons array instead of having an array or an empty
        writeitinstance = WriteItInstance.objects.all()[0]
        message_data = {
            'author_name' : 'Felipipoo',
            'subject': 'new message',
            'content': 'the content thing',
            'writeitinstance': '/api/v1/instance/{0}/'.format(writeitinstance.id),
            'persons': "all"
        }
        url = '/api/v1/message/'
        response = self.api_client.post(url, data = message_data, format='json', authentication=self.get_credentials())
        
        the_message = Message.objects.get(author_name='Felipipoo')

        self.assertEquals(len(the_message.people), writeitinstance.persons.count())
        self.assertEquals(the_message.people,list(writeitinstance.persons.all()))

from nuntium.api import AnswerResource
from django.http import HttpRequest
from nuntium.models import Answer
class AnswersResourceTestCase(ResourceTestCase):
    def setUp(self):
        super(AnswersResourceTestCase,self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.answer = Answer.objects.all()[0]


    def test_resource_get_all_answers(self):
        resource = AnswerResource()
        self.assertTrue(resource)

        request = HttpRequest()
        answers_json = self.deserialize(resource.get_list(request))['objects']
        self.assertEquals(len(answers_json), Answer.objects.count())
        self.assertEquals(answers_json[0]["id"], self.answer.id)

from nuntium.models import OutboundMessage, OutboundMessageIdentifier, Answer

class AnswerCreationResource(ResourceTestCase):
    def setUp(self):
        super(AnswerCreationResource, self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.outbound_message = OutboundMessage.objects.all()[0]
        self.identifier = OutboundMessageIdentifier.objects.get(outbound_message=self.outbound_message)
        self.api_client = TestApiClient()
        self.user = User.objects.all()[0]
        self.data = {'format': 'json', 'username': self.user.username, 'api_key':self.user.api_key.key}

    def get_credentials(self):
        credentials = self.create_apikey(username=self.user.username, api_key=self.user.api_key.key)
        return credentials


    def test_I_can_create_an_answer_with_only_an_identifier_and_a_content(self):
        url = '/api/v1/create_answer/'
        content = 'Fiera tiene una pulga'
        answer_data = {
        'key':self.identifier.key,
        'content':content
        }
        previous_answers = Answer.objects.count()
        response = self.api_client.post(url, data = answer_data, format='json', authentication=self.get_credentials())
        self.assertHttpCreated(response)

        answers_count = Answer.objects.count()

        self.assertEquals(answers_count, previous_answers + 1)


    def test_authorization_using_api_key(self):
        url = '/api/v1/create_answer/'
        content = 'una sola'
        answer_data = {
        'key':self.identifier.key,
        'content':content
        }
        response = self.api_client.post(url, data = answer_data, format='json')
        self.assertHttpUnauthorized(response)

    def test_only_the_owner_can_create_an_answer(self):
        not_the_owner = User.objects.create(username='not_the_owner')
        his_api_key = not_the_owner.api_key
        credentials = self.create_apikey(username=not_the_owner.username, api_key=his_api_key.key)
        url = '/api/v1/create_answer/'
        content = 'una sola'
        answer_data = {
        'key':self.identifier.key,
        'content':content
        }

        response = self.api_client.post(url, data = answer_data, format='json', authentication=credentials)
        self.assertHttpUnauthorized(response)


    def test_only_post_endpoint(self):
        url = '/api/v1/create_answer/'
        content = 'una sola'
        answer_data = {
            'key':self.identifier.key,
            'content':content
        }
        response = self.api_client.get(url)
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.put(url, data = answer_data)
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.patch(url, data = answer_data)
        self.assertHttpMethodNotAllowed(response)


class HandleBounces(ResourceTestCase):
    def setUp(self):
        super(HandleBounces, self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.api_client = TestApiClient()
        self.user = User.objects.all()[0]
        self.outbound_message = OutboundMessage.objects.all()[0]
        self.identifier = OutboundMessageIdentifier.objects.get(outbound_message=self.outbound_message)

    def get_credentials(self):
        credentials = self.create_apikey(username=self.user.username, api_key=self.user.api_key.key)
        return credentials

    def test_handle_bounces_endpoint(self):
        url = '/api/v1/handle_bounce/'
        bounce_data = {
        'key':self.identifier.key
        }
        resp = self.api_client.post(url, data=bounce_data, authentication=self.get_credentials())
        self.assertHttpCreated(resp)

    def test_handle_bounces_sets_the_contact_to_bounced(self):
        url = '/api/v1/handle_bounce/'
        bounce_data = {
        'key':self.identifier.key
        }
        resp = self.api_client.post(url, data=bounce_data, authentication=self.get_credentials())


        self.assertTrue(self.outbound_message.contact.is_bounced)




