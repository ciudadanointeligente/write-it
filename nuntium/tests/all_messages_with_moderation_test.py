# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from instance.models import WriteItInstance
from ..models import Message, Moderation
from popolo.models import Person
from django.core import mail


class AllMessagesWithModerationInAWriteItInstances(TestCase):
    def setUp(self):
        super(AllMessagesWithModerationInAWriteItInstances, self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.get(id=1)
        self.writeitinstance1.config.moderation_needed_in_all_messages = True
        self.writeitinstance1.save()
        self.person1 = Person.objects.get(id=1)
        self.message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Subject 1',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

    def test_a_message_is_considered_not_moderated(self):
        self.assertFalse(self.message.moderated is None)
        self.assertFalse(self.message.moderated)

    def test_a_message_moderated_status_is_changed(self):
        self.message.moderated = True
        self.message.save()

        message = Message.objects.get(id=self.message.id)

        self.assertTrue(message.moderated)

    def test_a_message_does_not_have_a_moderation_previous_to_confirmation(self):
        self.assertEquals(Moderation.objects.filter(message=self.message).count(), 0)

    def test_when_you_create_a_public_message_in_the_instance(self):
        self.assertEquals(len(mail.outbox), 0)
        # the message is confirmated
        self.message.recently_confirmated()

        self.assertFalse(self.message.moderation is None)
        self.assertEquals(len(mail.outbox), 1)
        # the second should be the confirmation thing
        # just to make sure
        self.assertModerationMailSent(self.message, mail.outbox[0])
