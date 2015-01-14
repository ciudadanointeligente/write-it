# coding=utf8
from global_test_case import GlobalTestCase as TestCase
from global_test_case import ResourceGlobalTestCase as ResourceTestCase
import os
import logging
from mailit.models import RawIncomingEmail
from ..bin.handleemail import EmailHandler

class IncomingRawEmailTestCase(TestCase):
    def setUp(self):
        super(IncomingRawEmailTestCase, self).setUp()

    def test_create_one(self):
        '''Instanciate an incoming raw email'''
        f = open('mailit/tests/fixture/mail.txt')
        email_content = f.readlines()
        f.close()
        raw_email = RawIncomingEmail(content=email_content)
        self.assertTrue(raw_email)
        self.assertEquals(raw_email.content, email_content)
        
    def test_it_automatically_saves(self):
        '''It automatically saves the answer when an incoming email arrives'''
        f = open('mailit/tests/fixture/mail.txt')
        email_content = f.readlines()
        f.close()
        handler = EmailHandler()
        answer = handler.handle(email_content)
        raw_emails = RawIncomingEmail.objects.all()
        self.assertTrue(raw_emails)
        self.assertTrue(raw_emails.filter(content=email_content))

