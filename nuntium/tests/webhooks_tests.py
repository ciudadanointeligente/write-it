# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from nuntium.models import Message, WriteItInstance, AnswerWebHook, Answer
from django.core.exceptions import ValidationError
from tastypie.models import ApiKey
from mock import patch

class PostMock():
    def __init__(self):
        self.status_code = 201


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
        #I thought that this could be very useful in case of security
        #so validate on the other side if that the payload is sent
        #from an instance that the owner created
            'user':{
                'username':self.writeitinstance.owner.username,
                'apikey':self.api_key.key
            },
            'payload':{
                'message_id':'/api/v1/message/{0}/'.format(message.id),
                'content':'holiwi',
                'person':pedro.name
            }
         

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
        #I thought that this could be very useful in case of security
        #so validate on the other side if that the payload is sent
        #from an instance that the owner created
            'user':{
                'username':self.writeitinstance.owner.username,
                'apikey':self.api_key.key
            },
            'payload':{
                'message_id':'/api/v1/message/{0}/'.format(message.id),
                'content':'holiwi',
                'person':pedro.name
            }
         

        }
        with patch('requests.post') as post:
            post.return_value = PostMock()
            answer = Answer.objects.create(content='holiwi', message=message, person=pedro)
            answer.save()
            post.assert_called_once_with(webhook.url, data=expected_payload)
