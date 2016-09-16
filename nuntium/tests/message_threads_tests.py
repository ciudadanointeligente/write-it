# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from subdomains.utils import reverse
from instance.models import WriteItInstance
from nuntium.models import Message
from popolo.models import Person

class MessagesThreadsTestCase(TestCase):
    def setUp(self):
        self.writeitinstance = WriteItInstance.objects.get(id=1)

    def test_get_the_url(self):
        url = reverse('message_threads', subdomain=self.writeitinstance.slug)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        public_messages = Message.public_objects.filter(writeitinstance=self.writeitinstance)
        self.assertEquals(len(response.context['message_list']), public_messages.count())

    def test_get_threads_with_wrong_instance_slug(self):
        url = reverse('message_threads', subdomain='wrong-slug')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_unmoderated_messages_not_included(self):
        url = reverse('message_threads', subdomain=self.writeitinstance.slug)
        recipient = Person.objects.first()
        Message.objects.create(
            writeitinstance=self.writeitinstance,
            public=True,
            confirmated=True,
            moderated=True,
            subject='m: yes, p: yes, c: yes',
            slug='m:yes, p:yes, c:yes',
            content='example content',
            author_name='Joe Bloggs',
            author_email='joe@example.com',
            persons=[recipient],
        )
        Message.objects.create(
            writeitinstance=self.writeitinstance,
            public=True,
            confirmated=True,
            moderated=None,
            subject='m: null, p: yes, c: yes',
            slug='m:null, p:yes, c:yes',
            content='example content',
            author_name='Joe Bloggs',
            author_email='joe@example.com',
            persons=[recipient],
        )
        Message.objects.create(
            writeitinstance=self.writeitinstance,
            public=True,
            confirmated=True,
            moderated=False,
            subject='m: no, p: yes, c: yes',
            slug='m:no, p:yes, c:yes',
            content='example content',
            author_name='Joe Bloggs',
            author_email='joe@example.com',
            persons=[recipient],
        )
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('m: yes, p: yes, c: yes', response.content)
        self.assertIn('m: null, p: yes, c: yes', response.content)
        self.assertNotIn('m: no, p: yes, c: yes', response.content)
