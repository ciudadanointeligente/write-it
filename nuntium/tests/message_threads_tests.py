# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from subdomains.utils import reverse
from instance.models import WriteItInstance
from nuntium.models import Message


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
