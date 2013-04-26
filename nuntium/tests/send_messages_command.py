from django.core.management import call_command
from global_test_case import GlobalTestCase as TestCase
from nuntium.models import Message, WriteItInstance, OutboundMessage, MessageRecord
from popit.models import Person, ApiInstance
from contactos.models import ContactType, Contact

class SendMessagesTestCaseTestCase(TestCase):
    def setUp(self):
        super(SendMessagesTestCaseTestCase,self).setUp()



    def test_send_mails_command(self):

        args = []
        opts = {}
        call_command('send_mails', *args, **opts)

        self.assertEquals(Message.objects.filter(status="new").count(), 0)
        self.assertEquals(Message.objects.filter(status="sent").count(), 2)