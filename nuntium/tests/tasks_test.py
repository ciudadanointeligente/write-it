# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from nuntium.models import OutboundMessage
from nuntium.tasks import send_mails_task
from mock import patch


class TasksTestCase(TestCase):

    def setUp(self):
        super(TasksTestCase,self).setUp()
        



    def test_it_sends_the_emails(self):
        for outbound_message in OutboundMessage.objects.all():
            outbound_message.status="ready"
            outbound_message.save()

        result = send_mails_task()

        self.assertEquals(OutboundMessage.objects.filter(status="new").count(), 0)
        self.assertEquals(OutboundMessage.objects.filter(status="sent").count(), 2)


    def test_it_logs_the_sending_of_emails(self):
        outbound_message = OutboundMessage.objects.all()[0]
        outbound_message.status =  'ready'
        outbound_message.save()


        with patch('logging.info') as info:
            info.return_value = None

            expected_log = 'Sending a message to %(contact)s'
            expected_log = expected_log % {
            'contact':outbound_message.contact.value
            }
            

            result = send_mails_task()
            info.assert_called_with(expected_log)