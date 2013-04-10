from django.test import TestCase
from nuntium.models import Message, Instance
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from popit.models import Person, ApiInstance

class TestMessages(TestCase):

    def setUp(self):
        self.api_instance1 = ApiInstance.objects.create(url='http://popit.org/api/v1')
        self.api_instance2 = ApiInstance.objects.create(url='http://popit.org/api/v2')
        self.person = Person.objects.create(api_instance=self.api_instance1, name= 'Person 1')

    def test_create_message(self):
        instance = Instance.objects.create(name='instance 1', api_instance= self.api_instance1)
        message = Message.objects.create(content = 'Content 1', subject='Subject 1', instance= instance)
        self.assertTrue(message)
        #Validation test pending
        # self.assertRaises(ValidationError, Message, content='Content') # subject missing
        # self.assertRaises(ValidationError, Message, subject = 'Subject') # url missing


