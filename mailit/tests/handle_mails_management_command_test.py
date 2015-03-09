# coding=utf8
from global_test_case import GlobalTestCase as TestCase
from django.core.management import call_command
from ..management.commands.handleemail import AnswerForManageCommand
from nuntium.models import OutboundMessage, OutboundMessageIdentifier, Answer
from mock import patch
from django.core import mail
from django.test.utils import override_settings
from django.utils.unittest import skip


class ManagementCommandAnswer(TestCase):
    def setUp(self):
        super(ManagementCommandAnswer, self).setUp()

    def test_create_answer_for_management_command(self):
        email_answer = AnswerForManageCommand()
        email_answer.subject = 'prueba4'
        email_answer.content_text = 'prueba4lafieritaespeluda'
        email_answer.outbound_message_identifier = '8974aabsdsfierapulgosa'
        email_answer.email_from = 'falvarez@votainteligente.cl'
        email_answer.when = 'Wed Jun 26 21:05:33 2013'

        self.assertTrue(email_answer)
        self.assertEquals(email_answer.subject, 'prueba4')
        self.assertEquals(email_answer.content_text, 'prueba4lafieritaespeluda')
        self.assertEquals(email_answer.outbound_message_identifier, '8974aabsdsfierapulgosa')
        self.assertEquals(email_answer.email_from, 'falvarez@votainteligente.cl')
        self.assertEquals(email_answer.when, 'Wed Jun 26 21:05:33 2013')
        self.assertFalse(email_answer.is_bounced)


class ManagementCommandAnswerBehaviour(TestCase):
    def setUp(self):
        super(ManagementCommandAnswerBehaviour, self).setUp()
        self.outbound_message = OutboundMessage.objects.all()[0]
        self.identifier = self.outbound_message.outboundmessageidentifier
        self.email_answer = AnswerForManageCommand()
        self.email_answer.subject = 'prueba4'
        self.email_answer.content_text = 'prueba4lafieritaespeluda'
        self.email_answer.outbound_message_identifier = self.identifier.key
        self.email_answer.email_from = 'falvarez@votainteligente.cl'
        self.email_answer.when = 'Wed Jun 26 21:05:33 2013'

    def test_it_creates_an_answer_when_sent_back(self):
        self.assertEquals(Answer.objects.filter(message=self.outbound_message.message).count(), 0)
        self.email_answer.save()
        the_answer = Answer.objects.get(message=self.outbound_message.message)

        self.assertEquals(the_answer.content, self.email_answer.content_text)
        self.assertEquals(the_answer.person, self.outbound_message.contact.person)

    def test_it_invalidates_a_contact(self):
        self.email_answer.report_bounce()

        self.assertTrue(self.outbound_message.contact.is_bounced)

    def test_it_sets_the_outbound_message_to_error(self):
        self.email_answer.report_bounce()
        outbound_message = OutboundMessage.objects.get(id=self.outbound_message.id)
        self.assertEquals(outbound_message.status, 'error')

    def test_it_handles_bounces_in_send_back_function(self):
        #the email is a bounce
        self.email_answer.is_bounced = True
        self.email_answer.send_back()

        self.assertTrue(self.outbound_message.contact.is_bounced)

    def test_it_does_not_create_an_answer_when_it_is_a_bounce(self):
        self.email_answer.is_bounced = True
        self.email_answer.send_back()

        self.assertEquals(Answer.objects.filter(message=self.outbound_message.message).count(), 0)

    def test_it_creates_an_answer_when_is_not_bounced(self):
        #the email is not a bounce
        self.assertEquals(Answer.objects.filter(message=self.outbound_message.message).count(), 0)
        self.email_answer.send_back()
        the_answer = Answer.objects.get(message=self.outbound_message.message)

        self.assertEquals(the_answer.content, self.email_answer.content_text)
        self.assertEquals(the_answer.person, self.outbound_message.contact.person)


def readlines1_mock():
    file_name = 'mailit/tests/fixture/mail.txt'
    f = open(file_name)
    lines = f.readlines()
    f.close()
    return lines


def readlines2_mock():
    file_name = 'mailit/tests/fixture/mail_with_identifier_in_the_content.txt'
    f = open(file_name)
    lines = f.readlines()
    f.close()
    return lines


def readlines3_mock():
    file_name = 'mailit/tests/fixture/mail_for_no_message.txt'
    f = open(file_name)
    lines = f.readlines()
    f.close()
    return lines


def readlines4_mock():
    file_name = 'mailit/tests/fixture/mail_with_unknown_content_type.txt'
    f = open(file_name)
    lines = f.readlines()
    f.close()
    return lines


class HandleIncomingEmailCommand(TestCase):
    def setUp(self):
        super(HandleIncomingEmailCommand, self).setUp()

    def test_call_command(self):
        identifier = OutboundMessageIdentifier.objects.all()[0]
        identifier.key = '4aaaabbb'
        identifier.save()

        with patch('sys.stdin') as stdin:
            stdin.attach_mock(readlines1_mock, 'readlines')

            call_command('handleemail', 'mailit.tests.handle_mails_management_command.StdinMock', verbosity=0)

            the_answers = Answer.objects.filter(message=identifier.outbound_message.message)
            self.assertEquals(the_answers.count(), 1)
            the_answer = the_answers[0]
            self.assertEquals(the_answer.content, 'prueba4lafieri\n')

            self.assertTrue(the_answer.content_html)
            self.assertIn('prueba4lafieri', the_answer.content_html)

    @override_settings(ADMINS=(('Felipe', 'falvarez@admins.org'),))
    def test_content_type_not_handed_email_admins(self):
        '''Email the admins if there is an email with a part that could not be handled'''
        identifier = OutboundMessageIdentifier.objects.all()[0]
        identifier.key = '4aaaabbb'
        identifier.save()

        with patch('sys.stdin') as stdin:
            stdin.attach_mock(readlines4_mock, 'readlines')
            call_command('handleemail', 'mailit.tests.handle_mails_management_command.StdinMock', verbosity=0)

            self.assertTrue(len(mail.outbox) > 0)
            email = mail.outbox[0]
            self.assertEquals(email.to, ['falvarez@admins.org'])
            self.assertIn("prueba4lafieri", email.body)
            self.assertIn("Content-Type: text/non-standard", email.body)

    @skip("I cant' figure out how to parse only the important part of an html response, #571")
    def test_get_the_right_html_part_of_the_email(self):
        '''Get the content of the email without the signature'''
        identifier = OutboundMessageIdentifier.objects.all()[0]
        identifier.key = '4aaaabbb'
        identifier.save()
        with patch('sys.stdin') as stdin:
            stdin.attach_mock(readlines1_mock, 'readlines')

            call_command('handleemail', 'mailit.tests.handle_mails_management_command.StdinMock', verbosity=0)

            the_answer = Answer.objects.get(message=identifier.outbound_message.message)

            self.assertEquals(the_answer.content_html, '<div dir="ltr">prueba4lafieri<br clear="all"><div><br>')

    def test_call_command_does_not_include_identifier_in_content(self):
        identifier = OutboundMessageIdentifier.objects.all()[0]
        identifier.key = '4aaaabbb'
        identifier.save()

        with patch('sys.stdin') as stdin:
            stdin.attach_mock(readlines2_mock, 'readlines')

            call_command('handleemail', 'mailit.tests.handle_mails_management_command.StdinMock', verbosity=0)

            the_answers = Answer.objects.filter(message=identifier.outbound_message.message)
            self.assertEquals(the_answers.count(), 1)
            self.assertFalse(identifier.key in the_answers[0].content)

    @override_settings(ADMINS=(('Felipe', 'falvarez@admins.org'),))
    def test_it_sends_an_email_to_the_admin_if_any_failure(self):
        with patch('sys.stdin') as stdin:
            stdin.attach_mock(readlines3_mock, 'readlines')
            call_command('handleemail', 'mailit.tests.handle_mails_management_command.StdinMock', verbosity=0)
            content_text = ''
            for line in readlines3_mock():
                content_text += line
            self.assertEquals(len(mail.outbox), 1)
            self.assertNotIn(content_text, mail.outbox[0].body)
            self.assertEquals(mail.outbox[0].to[0], 'falvarez@admins.org')
            self.assertEquals(len(mail.outbox[0].attachments), 1)
