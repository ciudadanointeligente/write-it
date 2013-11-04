# coding=utf8
from global_test_case import GlobalTestCase as TestCase
from django.core.management import call_command
from mailit.management.commands.handleemail import AnswerForManageCommand
from nuntium.models import OutboundMessage, OutboundMessageIdentifier, Answer
from django.utils.unittest import skip
from mock import patch, Mock
from django.core import mail
from django.test.utils import override_settings

def readlines1_mock():
    file_name='mailit/tests/fixture/mail.txt'
    f = open(file_name)
    lines = f.readlines()
    f.close()
    return lines

class LoggingTests(TestCase):
    def setUp(self):
        super(LoggingTests, self).setUp()

    @override_settings(ADMINS=(('Felipe', 'falvarez@admins.org'),), INCOMING_EMAIL_LOGGING='ALL')
    def test_it_sends_a_mail_to_the_admins_when_receiving_a_mail(self):
        identifier = OutboundMessageIdentifier.objects.all()[0]
        identifier.key = '4aaaabbb'
        identifier.save()

        with patch('sys.stdin') as stdin:
            stdin.attach_mock(readlines1_mock,'readlines')
            
            call_command('handleemail','mailit.tests.handle_mails_management_command.StdinMock', verbosity=0)

            self.assertEquals(len(mail.outbox), 1)
            self.assertEquals(mail.outbox[0].to[0],'falvarez@admins.org')
            self.assertEquals(len(mail.outbox[0].attachments), 1)
            the_file = mail.outbox[0].attachments[0]
            self.assertEquals(the_file[0], 'mail.txt')
            self.assertEquals(the_file[2], 'text/plain')