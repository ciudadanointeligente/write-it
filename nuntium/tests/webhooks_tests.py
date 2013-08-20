# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from nuntium.models import Message, WriteItInstance, AnswerWebHook
from django.core.exceptions import ValidationError

class NewAnswerWebhooks(TestCase):
    def setUp(self):
        super(NewAnswerWebhooks, self).setUp()
        self.writeitinstance = WriteItInstance.objects.all()[0]


    def test_creation_of_a_new_answer_webhook(self):
        
        webhook = AnswerWebHook.objects.create(
            writeitinstance=self.writeitinstance,
            url='http://someaddress.to.be.mocked'
            )

        self.assertTrue(webhook)
        self.assertEquals(webhook.writeitinstance, self.writeitinstance)
        self.assertEquals(webhook.url, 'http://someaddress.to.be.mocked')