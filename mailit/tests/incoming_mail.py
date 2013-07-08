# coding=utf8
from global_test_case import GlobalTestCase as TestCase
from global_test_case import ResourceGlobalTestCase as ResourceTestCase
import os
from mailit.bin.handleemail import EmailHandler, EmailAnswer, ApiKeyAuth
from django.utils.unittest import skip
from mock import patch
from django.contrib.auth.models import User
import requests
from requests.models import Request
from tastypie.models import ApiKey
import logging
from mailit.bin import config
import json

class PostMock():
    def __init__(self):
        self.status_code = 201


class TestApiKeyAuthentification(TestCase):
    def setUp(self):
        super(TestApiKeyAuthentification,self).setUp()
        self.user = User.objects.all()[0]
        self.api_key = ApiKey.objects.create(user=self.user)

    def test_creation(self):
        auth = ApiKeyAuth(username = self.user.username, api_key=self.api_key.key)
        self.assertTrue(auth)
        self.assertEquals(auth.username, self.user.username)
        self.assertEquals(auth.api_key, self.api_key.key)

    def test_set_headers(self):
        auth = ApiKeyAuth(username = self.user.username, api_key=self.api_key.key)
        req = Request()
        req = auth.__call__(req)
        self.assertTrue('Authorization' in req.headers)
        expected_headers = 'ApiKey %s:%s' % (self.user.username, self.api_key.key)
        self.assertEquals(req.headers['Authorization'], expected_headers)
            

class AnswerHandlerTestCase(TestCase):
    def setUp(self):
        super(AnswerHandlerTestCase,self).setUp()
        self.user = User.objects.all()[0]
        ApiKey.objects.create(user=self.user)
        self.where_to_post_creation_of_the_answer = 'http://writeit.ciudadanointeligente.org/api/v1/create_answer/'
        config.WRITEIT_API_ANSWER_CREATION = self.where_to_post_creation_of_the_answer
        config.WRITEIT_API_KEY = self.user.api_key.key
        config.WRITEIT_USERNAME = self.user.username


    def test_class_answer(self):

        email_answer = EmailAnswer()
        email_answer.subject = 'prueba4'
        email_answer.content_text = 'prueba4lafieritaespeluda'
        email_answer.outbound_message_identifier = '8974aabsdsfierapulgosa'
        email_answer.email_from = 'falvarez@votainteligente.cl'
        email_answer.when = 'Wed Jun 26 21:05:33 2013'


        self.assertTrue(email_answer)
        self.assertEquals(email_answer.subject, 'prueba4')
        self.assertEquals(email_answer.content_text, 'prueba4lafieritaespeluda')
        self.assertEquals(email_answer.outbound_message_identifier, '8974aabsdsfierapulgosa')
        self.assertEquals(email_answer.email_from, 'falvarez@votainteligente.cl')
        self.assertEquals(email_answer.when, 'Wed Jun 26 21:05:33 2013')

class ReplyHandlerTestCase(ResourceTestCase):
    def setUp(self):
        super(ReplyHandlerTestCase, self).setUp()
        self.user = User.objects.all()[0]
        ApiKey.objects.create(user=self.user)
        f = open('mailit/tests/fixture/reply_mail.txt')
        self.email = f.readlines()
        f.close()
        self.where_to_post_creation_of_the_answer = 'http://localhost:8000/api/v1/create_answer/'
        config.WRITEIT_API_ANSWER_CREATION = self.where_to_post_creation_of_the_answer
        config.WRITEIT_API_KEY = self.user.api_key.key
        config.WRITEIT_USERNAME = self.user.username
        self.handler = EmailHandler()

    #@skip("This test is currently failing reported in here https://github.com/zapier/email-reply-parser/issues/4 ")
    def test_get_only_new_content_and_not_original(self):
        self.answer = self.handler.handle(self.email)
        self.assertEquals(self.answer.content_text, u"aass áéíóúñ")



class IncomingEmailHandlerTestCase(ResourceTestCase):
    def setUp(self):
        super(IncomingEmailHandlerTestCase,self).setUp()
        self.user = User.objects.all()[0]
        ApiKey.objects.create(user=self.user)
        f = open('mailit/tests/fixture/mail.txt')
        self.email = f.readlines()
        f.close()
        self.where_to_post_creation_of_the_answer = 'http://localhost:8000/api/v1/create_answer/'
        config.WRITEIT_API_ANSWER_CREATION = self.where_to_post_creation_of_the_answer
        config.WRITEIT_API_KEY = self.user.api_key.key
        config.WRITEIT_USERNAME = self.user.username
        self.handler = EmailHandler()

    def test_gets_the_subject(self):
        self.answer = self.handler.handle(self.email)
        self.assertEquals(self.answer.subject, 'prueba4')

    def test_gets_the_content(self):
        self.answer = self.handler.handle(self.email)
        self.assertTrue(self.answer.content_text.startswith('prueba4lafieri'))
        
    def test_gets_the_outbound_message_identifier_to_which_relate_it(self):
        #make a regexp
        #ask maugsbur about it
        self.answer = self.handler.handle(self.email)
        self.assertEquals(self.answer.outbound_message_identifier,"4aaaabbb")

    def test_gets_who_sent_the_email(self):
        self.answer = self.handler.handle(self.email)
        self.assertEquals(self.answer.email_from, '=?ISO-8859-1?Q?Felipe_=C1lvarez?= <falvarez@ciudadanointeligente.cl>')

    def test_gets_when_it_was_sent(self):
        self.answer = self.handler.handle(self.email)
        self.assertEquals(self.answer.when, 'Wed, 26 Jun 2013 17:05:30 -0400')


    def test_it_posts_to_the_api(self):
        self.answer = self.handler.handle(self.email)
        self.assertEquals(self.answer.requests_session.auth.api_key, self.user.api_key.key)
        self.assertEquals(self.answer.requests_session.auth.username, self.user.username)
        expected_headers = {'content-type': 'application/json'}
        data = {
        'key':self.answer.outbound_message_identifier,
        'content':self.answer.content_text,
        'format': 'json'
        }
        data = json.dumps(data)
        with patch('requests.Session.post') as post:
            post.return_value = PostMock()
            self.answer.send_back()

            post.assert_called_with(self.where_to_post_creation_of_the_answer, data=data, headers=expected_headers)


    def test_logs_the_result_of_send_back(self):
        

        email_answer = EmailAnswer()
        email_answer.subject = 'prueba4'
        email_answer.content_text = 'prueba4lafieritaespeluda'
        email_answer.outbound_message_identifier = '8974aabsdsfierapulgosa'
        email_answer.email_from = 'falvarez@votainteligente.cl'
        email_answer.when = 'Wed Jun 26 21:05:33 2013'
        with patch('logging.info') as info:
            info.return_value = None
            with patch('requests.Session.post') as post:
                post.return_value = PostMock()

                with patch('logging.info') as info:
                    expected_log = "When sent to %(location)s the status code was 201" % { 
                        'location': self.where_to_post_creation_of_the_answer 
                    }
                    email_answer.send_back()
                    info.assert_called_with(expected_log)





    def test_logs_the_incoming_email(self):

        with patch('logging.info') as info:
            info.return_value = None
            
            self.answer = self.handler.handle(self.email)
            expected_log = 'New incoming email from %(from)s sent on %(date)s with subject %(subject)s and content %(content)s'
            expected_log = expected_log % {
            'from':self.answer.email_from,
            'date':self.answer.when,
            'subject':self.answer.subject,
            'content':self.answer.content_text
            }
            info.assert_called_with(expected_log)


