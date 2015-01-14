# coding=utf8
from global_test_case import GlobalTestCase as TestCase
from global_test_case import ResourceGlobalTestCase as ResourceTestCase
import os
import logging
from mailit.models import RawIncomingEmail
from ..bin.handleemail import EmailHandler
from nuntium.models import WriteItInstance, Answer, OutboundMessageIdentifier, OutboundMessage
from ..bin import config
from django.contrib.auth.models import User
from mailit.bin.handleemail import EmailAnswer
from django.utils.unittest import skip


class AnswerForThisTestCase(EmailAnswer):
    def save(self):
        OutboundMessageIdentifier.create_answer(self.outbound_message_identifier, self.content_text)

    def report_bounce(self):
        pass


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
        instance = WriteItInstance.objects.all()[0]
        raw_email = RawIncomingEmail(content=self.email_content)
        raw_email.writeitinstance = instance
        raw_email.save()

        instance = WriteItInstance.objects.get(id=instance.id)
        raw_emails = instance.raw_emails.all()

        self.assertTrue(raw_emails)
        self.assertIn(raw_email, raw_emails)

    def test_can_be_related_to_an_answe(self):
        '''A raw mail can be related to an answer'''
        answer = Answer.objects.all()[0]
        with self.assertRaises(RawIncomingEmail.DoesNotExist) as error:
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
        self.user = User.objects.all()[0]
        self.where_to_post_creation_of_the_answer = 'http://testserver/api/v1/create_answer/'
        config.WRITEIT_API_ANSWER_CREATION = self.where_to_post_creation_of_the_answer
        config.WRITEIT_API_KEY = self.user.api_key.key
        config.WRITEIT_USERNAME = self.user.username

        self.set_email_content()

        self.outbound_message = OutboundMessage.objects.all()[0]
        self.identifier = self.outbound_message.outboundmessageidentifier
        self.identifier.key = "4aaaabbb"
        self.identifier.save()

    def test_it_automatically_saves(self):
        '''It automatically saves the answer when an incoming email arrives'''
        handler = EmailHandler()
        answer = handler.handle(self.email_content)
        raw_emails = RawIncomingEmail.objects.all()
        self.assertTrue(raw_emails)
        self.assertTrue(raw_emails.filter(content=self.email_content))
    
    @skip('Need to find a way to find what answer was created based on this email')
    def test_it_relates_it_to_an_answer(self):
        '''After handling email the answer should be related'''

        handler = EmailHandler(answer_class = AnswerForThisTestCase)
        email_answer = handler.handle(self.email_content)
        email_answer.send_back()
        answer = Answer.objects.get(message=self.outbound_message.message)

        raw_emails = RawIncomingEmail.objects.filter(answer=answer)
        self.assertTrue(raw_emails)
        self.assertEquals(raw_emails.count(), 1)
        raw_email = raw_emails[0]
        self.assertEquals(raw_email.content, self.email_content)


