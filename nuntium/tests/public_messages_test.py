# -*- coding: utf-8 -*-
from django.core.management import call_command
from global_test_case import GlobalTestCase as TestCase
from instance.models import WriteItInstance
from ..models import Message, Confirmation
from popolo.models import Person
from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase, TestApiClient


class NonModeratedMessagesManagerTestCase(TestCase):
    def setUp(self):
        super(NonModeratedMessagesManagerTestCase, self).setUp()
        self.moderation_not_needed_instance = WriteItInstance.objects.get(id=1)
        self.person1 = Person.objects.get(id=1)
        self.moderable_instance = WriteItInstance.objects.get(id=2)
        self.moderable_instance.config.moderation_needed_in_all_messages = True

        self.moderable_instance.config.save()

    def test_it_has_a_manager_for_needing_moderation_messages(self):
        """There is a manager for the Message model that shows only the messages that need moderation"""
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='public non moderated message',
            writeitinstance=self.moderable_instance,
            persons=[self.person1],
            )
        Confirmation.objects.create(message=message)
        self.assertNotIn(message, Message.moderation_required_objects.all())

        message.recently_confirmated()

        self.assertIn(message, Message.moderation_required_objects.all())


class PublicMessagesManager(TestCase):
    def setUp(self):
        super(PublicMessagesManager, self).setUp()
        self.moderation_not_needed_instance = WriteItInstance.objects.get(id=1)
        self.person1 = Person.objects.get(id=1)
        self.moderable_instance = WriteItInstance.objects.get(id=2)
        self.moderable_instance.config.moderation_needed_in_all_messages = True

        self.moderable_instance.config.save()

    def test_public_non_confirmated_message_is_not_in_the_public(self):
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='public non confirmated message',
            writeitinstance=self.moderation_not_needed_instance,
            persons=[self.person1],
            )
        Confirmation.objects.create(message=message)

        self.assertNotIn(message, Message.public_objects.all())

        message.recently_confirmated()

        self.assertIn(message, Message.public_objects.all())

    def test_confirmated_but_non_moderated_message_in_a_moderable_instance_is_not_shown(self):
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='public non confirmated message',
            writeitinstance=self.moderable_instance,
            persons=[self.person1],
            )

        Confirmation.objects.create(message=message)
        self.assertNotIn(message, Message.public_objects.all())
        message.recently_confirmated()

        # the important one
        self.assertNotIn(message, Message.public_objects.all())


class PublicMessagesInAPI(ResourceTestCase):
    def setUp(self):
        super(PublicMessagesInAPI, self).setUp()
        call_command('loaddata', 'example_data', verbosity=0)
        self.user = User.objects.get(id=1)
        self.writeitinstance = WriteItInstance.objects.create(name="a test", slug="a-test", owner=self.user)
        self.writeitinstance.config.moderation_needed_in_all_messages = True
        self.writeitinstance.config.save()
        self.person1 = Person.objects.get(id=1)
        self.api_client = TestApiClient()
        self.data = {'format': 'json', 'username': self.user.username, 'api_key': self.user.api_key.key}

    def test_non_confirmated_message_not_showing_in_api(self):
        """Non confirmated message is not in the API"""

        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='public non confirmated message',
            writeitinstance=self.writeitinstance,
            persons=[self.person1],
            )

        # OK this is just to show that this message is not confirmed
        self.assertFalse(message.confirmated)
        self.assertNotIn(message, Message.public_objects.all())
        # I've tested this in messages_test.py

        url = '/api/v1/instance/{0}/messages/'.format(self.writeitinstance.id)
        response = self.api_client.get(url, data=self.data)
        self.assertValidJSONResponse(response)
        messages = self.deserialize(response)['objects']
        self.assertFalse(messages)
