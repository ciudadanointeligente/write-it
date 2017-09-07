# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from mailit.models import RawIncomingEmail
from ..bin.handleemail import EmailHandler
from instance.models import WriteItInstance
from nuntium.models import Answer, OutboundMessage
from ..bin import config
from django.contrib.auth.models import User
from mailit.bin.handleemail import EmailAnswer
from mailit.management.commands.handleemail import AnswerForManageCommand
from mock import patch


class IncomingRawEmailMixin():
    def set_email_content(self):
        f = open('mailit/tests/fixture/mail.txt')
        self.email_content = f.readlines()
        f.close()


class IncomingRawEmailTestCase(TestCase, IncomingRawEmailMixin):
    def setUp(self):
        super(IncomingRawEmailTestCase, self).setUp()
        self.set_email_content()

    def test_create_one(self):
        '''Instanciate an incoming raw email'''
        raw_email = RawIncomingEmail(content=self.email_content)

        self.assertTrue(raw_email)
        self.assertEquals(raw_email.content, self.email_content)
        self.assertFalse(raw_email.problem)
        self.assertFalse(raw_email.message_id)

    def test_it_relates_the_raw_mail_to_an_instance(self):
        '''The raw message can be related to an instance'''
        instance = WriteItInstance.objects.get(id=1)
        raw_email = RawIncomingEmail(content=self.email_content)
        raw_email.writeitinstance = instance
        raw_email.save()

        instance = WriteItInstance.objects.get(id=instance.id)
        raw_emails = instance.raw_emails.all()

        self.assertTrue(raw_emails)
        self.assertIn(raw_email, raw_emails)

    def test_can_be_related_to_an_answe(self):
        '''A raw mail can be related to an answer'''
        answer = Answer.objects.get(id=1)
        with self.assertRaises(RawIncomingEmail.DoesNotExist):
            answer.raw_email
        raw_email = RawIncomingEmail(content=self.email_content)
        raw_email.answer = answer
        raw_email.save()

        answer = Answer.objects.get(id=answer.id)
        self.assertTrue(answer.raw_email)
        self.assertEquals(answer.raw_email, raw_email)


class IncomingEmailAutomaticallySavesRawMessage(TestCase, IncomingRawEmailMixin):
    def setUp(self):
        super(IncomingEmailAutomaticallySavesRawMessage, self).setUp()
        self.user = User.objects.get(id=1)
        self.where_to_post_creation_of_the_answer = 'http://testserver/api/v1/create_answer/'
        config.WRITEIT_API_ANSWER_CREATION = self.where_to_post_creation_of_the_answer
        config.WRITEIT_API_KEY = self.user.api_key.key
        config.WRITEIT_USERNAME = self.user.username

        self.set_email_content()

        self.outbound_message = OutboundMessage.objects.get(id=1)
        self.identifier = self.outbound_message.outboundmessageidentifier
        self.identifier.key = "4aaaabbb"
        self.identifier.save()

    def test_it_automatically_saves(self):
        '''It automatically saves the answer when an incoming email arrives'''
        handler = EmailHandler()
        handler.handle(self.email_content)
        raw_emails = RawIncomingEmail.objects.all()
        self.assertTrue(raw_emails)
        self.assertTrue(raw_emails.filter(content=self.email_content))

    def test_it_sets_the_message_id(self):
        '''It automatically saves the answer when an incoming email arrives'''
        handler = EmailHandler()
        handler.handle(self.email_content)
        raw_emails = RawIncomingEmail.objects.filter(message_id='<CAA5PczfGfdhf29wgK=8t6j7hm8HYsBy8Qg87iTU2pF42Ez3VcQ@mail.gmail.com>')

        self.assertTrue(raw_emails)

    def test_it_relates_it_to_an_answer(self):
        '''After handling email the answer should be related'''

        handler = EmailHandler(answer_class=AnswerForManageCommand)
        email_answer = handler.handle(self.email_content)
        email_answer.send_back()
        raw_emails = RawIncomingEmail.objects.filter(message_id=email_answer.message_id)
        self.assertTrue(raw_emails)
        raw_email = raw_emails[0]
        # now making sure that it created an answer
        answer = Answer.objects.get(message=self.outbound_message.message)
        self.assertIsNotNone(raw_email.answer)
        self.assertEquals(raw_email.answer, answer)

    def test_if_answer_is_none_then_it_does_not_store_it(self):
        '''If answer is none when saving then it keeps on being none'''
        class NotGoingToReturnAnyAnswer(EmailAnswer):
            def save(self):
                return None

        handler = EmailHandler(answer_class=NotGoingToReturnAnyAnswer)
        email_answer = handler.handle(self.email_content)
        email_answer.send_back()
        raw_email = RawIncomingEmail.objects.get(message_id=email_answer.message_id)
        self.assertIsNone(raw_email.answer)

    # @skip('gotta check API first, because it is not returning the answer')

    def mock_request_to_api(self):
        person = self.outbound_message.message.people.get(
            instancemembership__writeitinstance=self.outbound_message.message.writeitinstance,
            )

        answer = Answer.objects.create(
            message=self.outbound_message.message,
            person=person,
            )

        class PostMock():
            def __init__(self):
                self.status_code = 201
                self.content = '{"content": "Fiera tiene una pulga", "id": %(id)s, "key": "47bc10f49c3811e4a1f30026b6e903f7", "resource_uri": "/api/v1/create_answer/%(id)s/"}' % {'id': answer.id}

        return PostMock

    def test_it_relates_to_an_answer_using_web_answer_creation(self):
        '''When creating an answer using the API then it also relates the answer to the raw email'''
        handler = EmailHandler()
        email_answer = handler.handle(self.email_content)
        post_mock = self.mock_request_to_api()
        with patch('requests.Session.post') as post:

            post.return_value = post_mock()
            email_answer.send_back()
        raw_emails = RawIncomingEmail.objects.filter(message_id=email_answer.message_id)
        self.assertTrue(raw_emails)
        raw_email = raw_emails[0]
        # now making sure that it created an answer
        answer = Answer.objects.get(message=self.outbound_message.message)
        self.assertIsNotNone(raw_email.answer)
        self.assertEquals(raw_email.answer, answer)
