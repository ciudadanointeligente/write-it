from django.test import TestCase
from nuntium.models import Instance, Message
from django.utils.unittest import skip

class InstanceTestCase(TestCase):

    def setUp(self):
        pass

    def test_create_instance(self):
        instance = Instance.objects.create(name='instance 1')
        self.assertTrue(instance)

    def test_instance_containning_several_messages(self):
        instance1 = Instance.objects.create(name='instance 1')
        instance2 = Instance.objects.create(name='instance 2')
        message1 = Message.objects.create(content='Content 1', subject='Subject 1', instance = instance1)
        message2 = Message.objects.create(content='Content 2', subject='Subject 2', instance = instance1)
        message3 = Message.objects.create(content='Content 3', subject='Subject 3', instance = instance2)
        self.assertEquals(instance1.message_set.count(),2)
        self.assertEquals(message1.instance, instance1)
        self.assertEquals(message2.instance, instance1)
        self.assertEquals(instance2.message_set.count(),1)
        self.assertEquals(message3.instance, instance2)
