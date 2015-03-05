# coding=utf8
from nuntium.models import OutboundMessage, OutboundMessageIdentifier
from mailit.management.commands.handleemail import AnswerForManageCommand
from global_test_case import GlobalTestCase as TestCase
from mailit.bin.handleemail import EmailHandler


class ParsingMailsWithAttachments(TestCase):
    def setUp(self):
        super(ParsingMailsWithAttachments, self).setUp()
        self.outbound_message = OutboundMessage.objects.get(id=1)
        self.identifier = OutboundMessageIdentifier.objects.get(id=1)
        self.identifier.key = '4aaaabbb'
        self.identifier.save()
        self.mail_with_attachments = ""
        with open('mailit/tests/fixture/mail_with_attachments.txt') as f:
            self.mail_with_attachments += f.read()
        f.close()
        self.handler = EmailHandler(answer_class=AnswerForManageCommand)

    def test_handle_mail_with_attachments(self):
        '''Handle mails with attachments creates some'''
        email_answer = self.handler.handle(self.mail_with_attachments)
        answer = email_answer.send_back()

        self.assertTrue(email_answer.attachments)
        self.assertTrue(answer.attachments.all())
