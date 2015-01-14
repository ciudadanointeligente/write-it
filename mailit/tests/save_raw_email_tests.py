# coding=utf8
from global_test_case import GlobalTestCase as TestCase
from global_test_case import ResourceGlobalTestCase as ResourceTestCase
import os
import logging
from mailit.models import RawIncomingEmail

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
        
