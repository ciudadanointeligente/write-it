# coding=utf-8
import re

from global_test_case import GlobalTestCase as TestCase
from instance.models import WriteItInstance
from ..models import Message, Confirmation
from popolo.models import Person
import datetime
from nuntium.views import MessageThreadView


class MessageDetailView(TestCase):
    def setUp(self):
        super(MessageDetailView, self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.get(id=1)
        self.person1 = Person.objects.get(id=1)
        self.message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Subject 1',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            confirmated=True,
            )
        Confirmation.objects.create(message=self.message, confirmated_at=datetime.datetime.now())
        self.anonymous_message = Message.objects.create(
            content='Content 2',
            author_name='',
            author_email="falvarez@votainteligente.cl",
            subject='Subject 2',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            confirmated=True,
            )
        Confirmation.objects.create(message=self.anonymous_message, confirmated_at=datetime.datetime.now())

    def test_get_message_detail_page(self):
        # I'm kind of feeling like I need
        # something like rspec or cucumber
        url = self.message.get_absolute_url()
        self.assertTrue(url)

        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['message'], self.message)

    def test_get_anonymous_message_detail_page(self):
        url = self.anonymous_message.get_absolute_url()
        self.assertTrue(url)

        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['message'], self.anonymous_message)

        match_anonymous_from = r'From</dt>\s+<dd>\s+Anonymous'
        self.assertTrue(re.search(match_anonymous_from, response.content))

        match_anonymous_title = r'An anonymous user sent a message to'
        self.assertTrue(re.search(match_anonymous_title, response.content))

    def test_get_message_detail_that_was_created_using_the_api(self):
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Subject 1',
            public=True,
            writeitinstance=self.writeitinstance1,
            confirmated=True,
            persons=[self.person1],
            )

        # this message is confirmated but has no confirmation object
        # this occurs when creating a message throu the API
        url = message.get_absolute_url()
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_get_messages_without_confirmation_and_not_confirmed(self):
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Subject 1',
            public=False,
            writeitinstance=self.writeitinstance1,
            confirmated=False,
            persons=[self.person1],
            )

        # this message is confirmated but has no confirmation object
        # this occurs when creating a message throu the API
        url = message.get_absolute_url()
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get_user_came_via_confirmation_link(self):
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Subject 1',
            writeitinstance=self.writeitinstance1,
            confirmated=True,
            persons=[self.person1],
            )
        request = self.factory.get(message.get_absolute_url())
        request.session = {'user_came_via_confirmation_link': True}
        view = MessageThreadView(request=request)
        view.object = message
        context = view.get_context_data()
        self.assertTrue(context['user_came_via_confirmation_link'])
