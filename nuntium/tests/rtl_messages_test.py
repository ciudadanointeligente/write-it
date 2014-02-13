# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from nuntium.models import Message, WriteItInstance
from popit.models import Person

class RTLTextInMessages(TestCase):
    def setUp(self):
        super(TestMessages,self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.person1 = Person.objects.all()[0]
        self.person2 = Person.objects.all()[1]

    def atest_fail(self):
    	self.fail()