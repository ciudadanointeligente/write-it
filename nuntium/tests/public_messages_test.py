# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from subdomains.tests import SubdomainTestMixin
from nuntium.models import WriteItInstance, Message, \
                            Confirmation
from popit.models import Person

class PublicMessagesManager(TestCase, SubdomainTestMixin):
    def setUp(self):
        super(PublicMessagesManager, self).setUp()
        self.moderation_not_needed_instance = WriteItInstance.objects.all()[0]
        self.person1 = Person.objects.all()[0]
        self.moderable_instance = WriteItInstance.objects.all()[1]
        self.moderable_instance.moderation_needed_in_all_messages = True

        self.moderable_instance.save()

    def test_public_non_confirmated_message_is_not_in_the_public(self):
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='public non confirmated message', 
            writeitinstance= self.moderation_not_needed_instance, 
            persons = [self.person1])
        Confirmation.objects.create(message=message)

        self.assertNotIn(message, Message.objects.public())

        message.recently_confirmated()

        self.assertIn(message, Message.objects.public())

    def test_confirmated_but_non_moderated_message_in_a_moderable_instance_is_not_shown(self):
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='public non confirmated message', 
            writeitinstance= self.moderable_instance, 
            persons = [self.person1])

        Confirmation.objects.create(message=message)
        self.assertNotIn(message, Message.objects.public())
        message.recently_confirmated()

        #the important one
        self.assertNotIn(message, Message.objects.public())