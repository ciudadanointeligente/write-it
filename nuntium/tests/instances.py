from django.test import TestCase
from nuntium.models import Instance, Message
from popit.models import ApiInstance, Person
from django.utils.unittest import skip

class InstanceTestCase(TestCase):

    def setUp(self):
        self.api_instance1 = ApiInstance.objects.create(url='http://popit.org/api/v1')
        self.api_instance2 = ApiInstance.objects.create(url='http://popit.org/api/v2')
        self.person = Person.objects.create(api_instance=self.api_instance1, name= 'Person 1')

    def test_create_instance(self):
        instance = Instance.objects.create(name='instance 1', api_instance= self.api_instance1)
        self.assertTrue(instance)

    def test_instance_containning_several_messages(self):
        instance1 = Instance.objects.create(name='instance 1', api_instance= self.api_instance1)
        instance2 = Instance.objects.create(name='instance 2', api_instance= self.api_instance2)
        message1 = Message.objects.create(content='Content 1', subject='Subject 1', instance = instance1)
        message2 = Message.objects.create(content='Content 2', subject='Subject 2', instance = instance1)
        message3 = Message.objects.create(content='Content 3', subject='Subject 3', instance = instance2)
        self.assertEquals(instance1.message_set.count(),2)
        self.assertEquals(message1.instance, instance1)
        self.assertEquals(message2.instance, instance1)
        self.assertEquals(instance2.message_set.count(),1)
        self.assertEquals(message3.instance, instance2)
