from django.test import TestCase
from django.core.management import call_command


class GlobalTestCase(TestCase):
    def setUp(self):
        call_command('loaddata', 'example_data', verbosity=0)

    def assertModerationMailSent(self, message, moderation_mail):
        self.assertEquals(moderation_mail.to[0], message.writeitinstance.owner.email)
        self.assertTrue(message.content in moderation_mail.body)
        self.assertTrue(message.subject in moderation_mail.body)
        self.assertTrue(message.author_name in moderation_mail.body)
        self.assertTrue(message.author_email in moderation_mail.body)
        for person in message.people:
            self.assertTrue(person.name in moderation_mail.body)
