from global_test_case import GlobalTestCase as TestCase
from global_test_case import ResourceGlobalTestCase as ResourceTestCase
import os
from mailit.bin import EmailHandler, EmailAnswer
from django.utils.unittest import skip
from mock import patch
from django.contrib.auth.models import User
import requests
from tastypie.models import ApiKey

class AnswerHandlerTestCase(TestCase):
    def setUp(self):
        super(AnswerHandlerTestCase,self).setUp()
        self.user = User.objects.all()[0]
        ApiKey.objects.create(user=self.user)
        self.where_to_post_creation_of_the_answer = 'http://writeit.ciudadanointeligente.org/api/v1/create_answer/'
        os.environ['WRITEIT_API_ANSWER_CREATION'] = self.where_to_post_creation_of_the_answer
        os.environ['WRITEIT_API_KEY'] = self.user.api_key.key
        os.environ['WRITEIT_USERNAME'] = self.user.username


    def test_class_answer(self):

        email_answer = EmailAnswer()
        email_answer.subject = 'prueba4'
        email_answer.content_text = 'prueba4lafieritaespeluda'
        email_answer.outbound_message_identifier = '8974aabsdsfierapulgosa'


        self.assertTrue(email_answer)
        self.assertEquals(email_answer.subject, 'prueba4')
        self.assertEquals(email_answer.content_text, 'prueba4lafieritaespeluda')
        self.assertEquals(email_answer.outbound_message_identifier, '8974aabsdsfierapulgosa')

class IncomingEmailHandlerTestCase(ResourceTestCase):
    def setUp(self):
        super(IncomingEmailHandlerTestCase,self).setUp()
        self.user = User.objects.all()[0]
        ApiKey.objects.create(user=self.user)
        f = open('mailit/tests/fixture/mail.txt')
        self.email = f.readlines()
        f.close()
        self.where_to_post_creation_of_the_answer = 'http://localhost:8000/api/v1/create_answer/'
        os.environ['WRITEIT_API_ANSWER_CREATION'] = self.where_to_post_creation_of_the_answer
        os.environ['WRITEIT_API_KEY'] = self.user.api_key.key
        os.environ['WRITEIT_USERNAME'] = self.user.username
        self.handler = EmailHandler()
        self.answer = self.handler.handle(self.email)
       

    def get_credentials(self):
        credentials = self.create_apikey(username=self.user.username, api_key=self.user.api_key.key)
        return credentials

    def test_gets_the_subject(self):
        self.assertEquals(self.answer.subject, 'prueba4')

    def test_gets_the_content(self):
        self.assertTrue(self.answer.content_text.startswith('prueba4lafieri'))
        
    def test_gets_the_outbound_message_identifier_to_which_relate_it(self):
        #make a regexp
        #ask maugsbur about it
        self.assertEquals(self.answer.outbound_message_identifier,"4aaaabbb")


    def test_it_posts_to_the_api(self):
        self.assertEquals(self.answer.requests_session.auth.api_key, self.user.api_key.key)
        self.assertEquals(self.answer.requests_session.auth.username, self.user.username)
        data = {
        'key':self.answer.outbound_message_identifier,
        'content':self.answer.content_text
        }
        with patch('requests.Session.post') as post:
            post.return_value = True
            self.answer.send_back()

            post.assert_called_with(self.where_to_post_creation_of_the_answer, data=data)


    # def test_this_one_is_not_mocked(self):
    #     credentials = self.get_credentials()
        
    #     self.assertEquals(self.answer.requests_session.auth.api_key, self.user.api_key.key)
    #     self.assertEquals(self.answer.requests_session.auth.username, self.user.username)
    #     data = {
    #     'key':self.answer.outbound_message_identifier,
    #     'content':self.answer.content_text
    #     }
    #     self.answer.send_back()


            




