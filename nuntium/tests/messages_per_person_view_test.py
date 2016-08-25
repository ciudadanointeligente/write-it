# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from subdomains.utils import reverse
from instance.models import PopoloPerson, WriteItInstance
from ..models import Message


class MessagesPerPersonViewTestCase(TestCase):
    def setUp(self):
        super(MessagesPerPersonViewTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.get(id=1)
        self.pedro = PopoloPerson.objects.get(name="Pedro")
        self.marcel = PopoloPerson.objects.get(name="Marcel")

    def test_has_an_url(self):
        url = reverse(
            'messages_per_person',
            subdomain=self.writeitinstance.slug,
            kwargs={
                'pk': self.pedro.id,
                }
            )

        self.assertTrue(url)

    def test_it_is_reachable(self):
        url = reverse(
            'thread_to',
            subdomain=self.writeitinstance.slug,
            kwargs={
                'pk': self.pedro.id,
                },
            )
        response = self.client.get(url)

        expected_messages = Message.objects.filter(
            person=self.pedro,
            confirmated=True,
            writeitinstance=self.writeitinstance,
            )

        self.assertEquals(response.status_code, 200)
        self.assertIn('person', response.context)
        self.assertEquals(response.context['person'], self.pedro)
        self.assertIn('message_list', response.context)
        self.assertQuerysetEqual(
            expected_messages,
            [repr(r) for r in response.context['message_list']],
            )

    def test_person_id_param(self):
        url = reverse(
            'messages_per_person_id',
            subdomain=self.writeitinstance.slug,
            kwargs={
                'person_id': self.pedro.popit_id,
                }
            )
        response = self.client.get(url)
        self.assertEquals(response.context['person'], self.pedro)

    def test_it_does_not_show_private_messages(self):
        private_message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Fiera es una perra feroz',
            writeitinstance=self.writeitinstance,
            public=False,
            confirmated=True,
            persons=[self.pedro],
            )
        private_message.moderate()

        # this private message should not be shown

        url = reverse(
            'thread_to',
            subdomain=self.writeitinstance.slug,
            kwargs={
                'pk': self.pedro.id,
                },
            )

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertNotIn(private_message, response.context['message_list'])

    def test_show_only_messages_that_are_related_to_the_writeitinstance(self):
        the_other_instance = WriteItInstance.objects.get(id=2)

        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Fiera es una perra feroz',
            writeitinstance=the_other_instance,
            public=True,
            confirmated=True,
            persons=[self.pedro],
            )
        url = reverse(
            'thread_to',
            subdomain=self.writeitinstance.slug,
            kwargs={
                'pk': self.pedro.id,
                },
            )

        response = self.client.get(url)

        # should not be here cause it belongs to other writeit instance
        self.assertNotIn(message, response.context['message_list'])

    def test_person_non_existing_throws_500(self):
        url = reverse(
            'thread_to',
            subdomain=self.writeitinstance.slug,
            kwargs={
                'pk': 1313,
                },
            )

        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_the_person_does_exist_but_not_the_instance(self):
        marcel = PopoloPerson.objects.get(id=2)
        url = reverse(
            'thread_to',
            subdomain='non-existing-slug',
            kwargs={
                'pk': marcel.id,
                },
            )
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)
