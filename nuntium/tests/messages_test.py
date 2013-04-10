from django.test import TestCase
from nuntium.models import Message, Instance
from django.core.exceptions import ValidationError
from django.db import IntegrityError

class TestMessages(TestCase):
    # def setUp(self):
    #     self.instance = ApiInstance(url="http://foo.com/api")
    #     self.person = Person(api_instance=self.instance, name="Bob")
    # we should wait for popit-django

    def test_create_message(self):
        instance = Instance.objects.create(name='instance 1')
        message = Message.objects.create(content = 'Content 1', subject='Subject 1', instance= instance)
        self.assertTrue(message)
        #Validation test pending
        # self.assertRaises(ValidationError, Message, content='Content') # subject missing
        # self.assertRaises(ValidationError, Message, subject = 'Subject') # url missing


