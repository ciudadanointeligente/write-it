# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from instance.models import WriteItInstance
from ..models import Message, AnswerWebHook, Answer
from mock import patch


class PostMock():
    def __init__(self):
        self.status_code = 201


class NewAnswerWebhooks(TestCase):
    def setUp(self):
        super(NewAnswerWebhooks, self).setUp()
        self.writeitinstance = WriteItInstance.objects.get(id=1)
        self.api_key = self.writeitinstance.owner.api_key

    def test_creation_of_a_new_answer_webhook(self):
        webhook = AnswerWebHook.objects.create(
            writeitinstance=self.writeitinstance,
            url='http://someaddress.to.be.mocked',
            )

        self.assertTrue(webhook)
        self.assertEquals(webhook.writeitinstance, self.writeitinstance)
        self.assertEquals(webhook.url, 'http://someaddress.to.be.mocked')
        self.assertIn(webhook, self.writeitinstance.answer_webhooks.all())

    def test_unicode(self):
        webhook = AnswerWebHook.objects.create(
            writeitinstance=self.writeitinstance,
            url='http://someaddress.to.be.mocked',
            )
        expected_unicode = '%(url)s at %(instance)s' % {
            'url': webhook.url,
            'instance': webhook.writeitinstance.name,
        }
        self.assertEquals(webhook.__unicode__(), expected_unicode)

    def test_when_a_new_answer_is_created_then_it_post_to_the_url(self):
        webhook = AnswerWebHook.objects.create(
            writeitinstance=self.writeitinstance,
            url='http://someaddress.to.be.mocked',
            )
        pedro = self.writeitinstance.persons.all()[0]
        # this message is the message to which we are going to create a new answer
        message = Message.objects.filter(writeitinstance=self.writeitinstance)[0]

        expected_payload = {
            'message_id': '/api/v1/message/{0}/'.format(message.id),
            'content': 'holiwi',
            'person': pedro.name,
            'person_id_in_popolo_source': pedro.id_in_popolo_source,
            'person_popolo_source_url': pedro.popolo_source_url,
            'person_id': pedro.uri_for_api(),
            }
        with patch('requests.post') as post:
            post.return_value = PostMock()
            Answer.objects.create(content='holiwi', message=message, person=pedro)
            post.assert_called_with(webhook.url, data=expected_payload)

    def test_it_does_not_send_the_payload_twice(self):
        """It doesn't send the payload twice"""
        webhook = AnswerWebHook.objects.create(
            writeitinstance=self.writeitinstance,
            url='http://someaddress.to.be.mocked'
            )
        pedro = self.writeitinstance.persons.all()[0]
        #this message is the message to which we are going to create a new answer
        message = Message.objects.filter(writeitinstance=self.writeitinstance)[0]

        expected_payload = {
            'message_id': '/api/v1/message/{0}/'.format(message.id),
            'content': 'holiwi',
            'person': pedro.name,
            'person_id_in_popolo_source': pedro.id_in_popolo_source,
            'person_popolo_source_url': pedro.popolo_source_url,
            'person_id': pedro.uri_for_api(),
            }
        with patch('requests.post') as post:
            post.return_value = PostMock()
            answer = Answer.objects.create(content='holiwi', message=message, person=pedro)
            answer.save()
            post.assert_called_once_with(webhook.url, data=expected_payload)
