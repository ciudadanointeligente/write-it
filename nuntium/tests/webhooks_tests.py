# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from nuntium.models import Message, WriteItInstance, AnswerWebHook, Answer, ApiKeyCredential, WebHookCredential
from django.core.exceptions import ValidationError
from tastypie.models import ApiKey
from mock import patch
from django.utils.unittest import skip
from django.db import models

class PostMock():
    def __init__(self):
        self.status_code = 201


class WebHookCredentialTestCase(TestCase):
    def setUp(self):
        super(WebHookCredentialTestCase, self).setUp()

    def test_it_is_not_an_abstract_class(self):
        #am I planning too much?

        instance = WebHookCredential.objects.create()

        self.assertTrue(instance)

    def test_it_has_method_get_auth(self):
        class TheCredential(WebHookCredential):
            pass

        instance = TheCredential()
        with self.assertRaises(NotImplementedError) as error:
            instance.get_auth()


class ApiKeyCredentials(TestCase):
    def setUp(self):
        super(ApiKeyCredentials, self).setUp()

    def test_create_model(self):
        api_key_credential = ApiKeyCredential.objects.create(username='admin', api_key='a')
        self.assertIsInstance(api_key_credential, WebHookCredential)

        self.assertTrue(api_key_credential)
        self.assertEquals(api_key_credential.username, 'admin')
        self.assertEquals(api_key_credential.api_key, 'a')


class NewAnswerWebhooks(TestCase):
    def setUp(self):
        super(NewAnswerWebhooks, self).setUp()
        self.writeitinstance = WriteItInstance.objects.all()[0]
        self.api_key = ApiKey.objects.create(user=self.writeitinstance.owner)


    def test_creation_of_a_new_answer_webhook(self):
        
        webhook = AnswerWebHook.objects.create(
            writeitinstance=self.writeitinstance,
            url='http://someaddress.to.be.mocked'
            )

        self.assertTrue(webhook)
        self.assertEquals(webhook.writeitinstance, self.writeitinstance)
        self.assertEquals(webhook.url, 'http://someaddress.to.be.mocked')
        self.assertIn(webhook, self.writeitinstance.answer_webhooks.all())

    def test_a_webhook_can_haz_an_api_key_credential(self):

        class AnyCredential(WebHookCredential):
            pass

        any_credential = AnyCredential()
        any_credential.id = 1

        webhook = AnswerWebHook.objects.create(
            writeitinstance=self.writeitinstance,
            url='http://someaddress.to.be.mocked',
            credential=any_credential
            )

        self.assertEquals(webhook.credential, any_credential)
        


    def test_unicode(self):
        webhook = AnswerWebHook.objects.create(
            writeitinstance=self.writeitinstance,
            url='http://someaddress.to.be.mocked'
            )
        expected_unicode = '%(url)s at %(instance)s'%{
        'url':webhook.url,
        'instance':webhook.writeitinstance.name
        }
        self.assertEquals(webhook.__unicode__(), expected_unicode)


    def test_when_a_new_answer_is_created_then_it_post_to_the_url(self):
        webhook = AnswerWebHook.objects.create(
            writeitinstance=self.writeitinstance,
            url='http://someaddress.to.be.mocked'
            )
        pedro = self.writeitinstance.persons.all()[0]
        #this message is the message to which we are going to create a new answer
        message = Message.objects.filter(writeitinstance=self.writeitinstance)[0]
        
        expected_payload = {
                'message_id':'/api/v1/message/{0}/'.format(message.id),
                'content':'holiwi',
                'person':pedro.name
        }
        with patch('requests.post') as post:
            post.return_value = PostMock()
            answer = Answer.objects.create(content='holiwi', message=message, person=pedro)
            post.assert_called_with(webhook.url, data=expected_payload)


    def test_it_does_not_send_the_payload_twice(self):
        webhook = AnswerWebHook.objects.create(
            writeitinstance=self.writeitinstance,
            url='http://someaddress.to.be.mocked'
            )
        pedro = self.writeitinstance.persons.all()[0]
        #this message is the message to which we are going to create a new answer
        message = Message.objects.filter(writeitinstance=self.writeitinstance)[0]
        
        expected_payload = {
                'message_id':'/api/v1/message/{0}/'.format(message.id),
                'content':'holiwi',
                'person':pedro.name
        }
        with patch('requests.post') as post:
            post.return_value = PostMock()
            answer = Answer.objects.create(content='holiwi', message=message, person=pedro)
            answer.save()
            post.assert_called_once_with(webhook.url, data=expected_payload)
