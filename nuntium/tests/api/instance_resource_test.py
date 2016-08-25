# -*- coding: utf-8 -*-
from django.core.management import call_command
from instance.models import WriteItInstance, PopoloPerson
from ...models import Message, Confirmation
from tastypie.test import ResourceTestCase, TestApiClient
from django.contrib.auth.models import User
from global_test_case import popit_load_data
from django.conf import settings
import re
from django.utils.encoding import force_text


class InstanceResourceTestCase(ResourceTestCase):
    def setUp(self):
        super(InstanceResourceTestCase, self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.user = User.objects.get(id=1)
        self.writeitinstance = WriteItInstance.objects.create(name=u"a test", slug=u"a-test", owner=self.user)
        self.api_client = TestApiClient()
        self.data = {'format': 'json', 'username': self.user.username, 'api_key': self.user.api_key.key}

    def get_credentials(self):
        credentials = self.create_apikey(username=self.user.username, api_key=self.user.api_key.key)
        return credentials

    def test_api_exists(self):
        url = '/api/v1/'
        resp = self.api_client.get(url, data=self.data)

        self.assertValidJSONResponse(resp)

    def test_api_needs_authentication(self):
        url = '/api/v1/instance/'
        response = self.api_client.get(url)

        self.assertHttpUnauthorized(response)

    def test_get_list_of_instances(self):
        url = '/api/v1/instance/'
        response = self.api_client.get(url, data=self.data)

        self.assertValidJSONResponse(response)

        instances = self.deserialize(response)['objects']
        self.assertEqual(len(instances), WriteItInstance.objects.count())  # All the instances
        first_instance = instances[0]
        self.assertEqual(first_instance['messages_uri'], '/api/v1/instance/{0}/messages/'.format(first_instance['id']))

    def test_get_detail_of_an_instance(self):
        url = '/api/v1/instance/{0}/'.format(self.writeitinstance.id)
        response = self.api_client.get(url, data=self.data)

        self.assertValidJSONResponse(response)

    def test_get_persons_of_an_instance(self):
        writeitinstance = WriteItInstance.objects.get(id=1)
        url = '/api/v1/instance/{0}/'.format(writeitinstance.id)
        response = self.api_client.get(url, data=self.data)
        instance = self.deserialize(response)
        self.assertIn('persons', instance)
        pedro = PopoloPerson.objects.get(id=1)
        self.assertIn(pedro.popit_url, instance['persons'])

    def test_create_a_new_instance(self):
        instance_data = {
            'name': 'The instance',
            'slug': 'the-instance',
        }
        url = '/api/v1/instance/'
        response = self.api_client.post(url, data=instance_data, format='json', authentication=self.get_credentials())
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

    @popit_load_data()
    def test_create_a_new_instance_with_only_name(self):
        instance_data = {
            'name': 'The instance',
        }
        url = '/api/v1/instance/'
        response = self.api_client.post(url, data=instance_data, format='json', authentication=self.get_credentials())
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
            'name': 'The instance',
            'slug': 'the-instance',
        }
        url = '/api/v1/instance/'
        response = self.api_client.post(url, data=instance_data, format='json')
        self.assertHttpUnauthorized(response)

    @popit_load_data()
    def test_create_and_pull_people_from_a_popit_api(self):
        # loading data into the popit-api

        instance_data = {
            'name': 'The instance',
            'slug': 'the-instance',
            'popit-api': settings.TEST_POPIT_API_URL,
        }
        url = '/api/v1/instance/'
        response = self.api_client.post(url, data=instance_data, format='json', authentication=self.get_credentials())
        self.assertHttpCreated(response)
        match_id = re.match(r'^http://testserver/api/v1/instance/(?P<id>\d+)/?', response['Location'])

        instance = WriteItInstance.objects.get(id=match_id.group('id'))
        self.assertEquals(instance.persons.count(), 2)
        #this should not break
        raton = PopoloPerson.objects.get(name=u'Ratón Inteligente')
        fiera = PopoloPerson.objects.get(name=u"Fiera Feroz")

        self.assertIn(raton, [r for r in instance.persons.all()])
        self.assertIn(fiera, [r for r in instance.persons.all()])


class MessagesPerInstanceTestCase(ResourceTestCase):
    def setUp(self):
        super(MessagesPerInstanceTestCase, self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.user = User.objects.get(id=1)
        self.writeitinstance = WriteItInstance.objects.create(name=u"a test", slug=u"a-test", owner=self.user)
        self.api_client = TestApiClient()
        self.data = {'format': 'json', 'username': self.user.username, 'api_key': self.user.api_key.key}

        # creating messages
        self.pedro = PopoloPerson.objects.get(id=1)
        self.writeitinstance.add_person(self.pedro)
        # Setting that the contact is related to self.writeitinstance rather than to the user
        self.contact = self.pedro.contact_set.all()[0]
        self.contact.writeitinstance = self.writeitinstance
        self.contact.save()

        self.message1 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Fiera es una perra feroz',
            writeitinstance=self.writeitinstance,
            persons=[self.pedro],
            )

        # Confirmating
        Confirmation.objects.create(message=self.message1)
        self.message1.recently_confirmated()
        # Confirmating

        self.marcel = PopoloPerson.objects.get(id=2)
        self.message2 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Fiera es una perra feroz',
            writeitinstance=self.writeitinstance,
            persons=[self.marcel],
            )
        # Confirmating message 2
        Confirmation.objects.create(message=self.message2)
        self.message2.recently_confirmated()
        # confirmating message 2

    def test_get_list_of_messages_per_instance(self):
        url = '/api/v1/instance/{0}/messages/'.format(self.writeitinstance.id)
        response = self.api_client.get(url, data=self.data)
        self.assertValidJSONResponse(response)
        messages = self.deserialize(response)['objects']

        self.assertGreater(len(messages), 0)
        filtered_messages = Message.objects.filter(writeitinstance=self.writeitinstance)
        self.assertEqual(len(messages), filtered_messages.count())  # All the instances

        self.assertTrue(filtered_messages.filter(id=messages[0]['id']))

        # assert that answers come in the

    def test_filter_by_person(self):
        url = '/api/v1/instance/%(writeitinstance_id)i/messages/' % {
            'writeitinstance_id': self.writeitinstance.id,
        }
        data = self.data
        data['person'] = self.pedro.id
        response = self.api_client.get(url, data=data)
        self.assertValidJSONResponse(response)
        messages = self.deserialize(response)['objects']

        self.assertEquals(len(messages), 1)
        self.assertEquals(messages[0]['id'], self.message1.id)

    def test_filter_by_persons_popit_id(self):
        url = '/api/v1/instance/%(writeitinstance_id)i/messages/' % {
            'writeitinstance_id': self.writeitinstance.id,
        }
        data = self.data
        data['person__popit_id'] = self.pedro.popit_id
        response = self.api_client.get(url, data=data)
        self.assertValidJSONResponse(response)
        messages = self.deserialize(response)['objects']

        self.assertEquals(len(messages), 1)
        self.assertEquals(messages[0]['id'], self.message1.id)

    def test_create_a_message_with_a_person_that_is_in_2_api_instances(self):
        api = PopitApiInstance.objects.create(id=3,
                                              url="https://popit.org/api/v1")
        p = PopoloPerson.objects.create(api_instance=api,
                                  name="Otro",
                                  popit_url="https://popit.org/api/v1/persons/1",
                                  popit_id="52bc7asdasd34567"
                                  )
        url = '/api/v1/instance/%(writeitinstance_id)i/messages/' % {
            'writeitinstance_id': self.writeitinstance.id,
        }
        data = self.data
        data['person__popit_id'] = p.popit_id
        response = self.api_client.get(url, data=data)
        self.assertValidJSONResponse(response)

    def test_it_raises_error_404_when_filtering_by_someone_that_doesnot_exist(self):
        url = '/api/v1/instance/%(writeitinstance_id)i/messages/' % {
            'writeitinstance_id': self.writeitinstance.id
        }
        data = self.data
        data['person__popit_id'] = "this-thing-does-not-exist"
        response = self.api_client.get(url, data=data)
        self.assertEquals(response.status_code, 404)

    def test_it_raises_error_404_when_filtering_by_person_id(self):
        url = '/api/v1/instance/%(writeitinstance_id)i/messages/' % {
            'writeitinstance_id': self.writeitinstance.id
        }
        data = self.data
        # person with id 42 does not exist
        data['person'] = 42
        # person with id 42 does not exist
        response = self.api_client.get(url, data=data)
        self.assertEquals(response.status_code, 404)
