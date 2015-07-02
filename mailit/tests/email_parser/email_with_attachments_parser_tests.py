# coding=utf-8
from nuntium.models import OutboundMessage
from mailit.management.commands.handleemail import AnswerForManageCommand
from global_test_case import GlobalTestCase as TestCase
from mailit.bin.handleemail import EmailHandler


class ParsingMailsWithAttachments(TestCase):
    def setUp(self):
        super(ParsingMailsWithAttachments, self).setUp()
        self.outbound_message = OutboundMessage.objects.get(id=1)
        self.outbound_message.outboundmessageidentifier.key = '4aaaabbb'
        self.outbound_message.outboundmessageidentifier.save()
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

    def test_attachments_with_names(self):
        '''When I get an attachment it should have names'''
        email_answer = self.handler.handle(self.mail_with_attachments)
        answer = email_answer.send_back()

        self.assertTrue(answer.attachments.filter(name="fiera_parque.jpg"))
        self.assertTrue(answer.attachments.filter(name="hello.pd.pdf"))
        self.assertTrue(answer.attachments.filter(name="hello.docx"))
