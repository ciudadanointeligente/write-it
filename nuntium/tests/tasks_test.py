# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from ..models import OutboundMessage
from ..tasks import send_mails_task
from mock import patch


class TasksTestCase(TestCase):

    def setUp(self):
        super(TasksTestCase,self).setUp()
        
    def test_it_has_a_name(self):
        self.assertEquals(send_mails_task.name,'nuntium.tasks.send_mails_task')



    def test_it_sends_the_emails(self):
        for outbound_message in OutboundMessage.objects.all():
            outbound_message.status="ready"
            outbound_message.save()

        result = send_mails_task()

        self.assertEquals(OutboundMessage.objects.filter(status="new").count(), 0)
        self.assertEquals(OutboundMessage.objects.filter(status="sent").count(), \
            OutboundMessage.objects.count())


    def test_it_logs_the_sending_of_emails(self):
        outbound_message = OutboundMessage.objects.all()[0]
        outbound_message.status =  'ready'
        outbound_message.save()


        with patch('logging.info') as info:
            info.return_value = None

            expected_log = 'Sending "%(message)s" to %(contact)s and the result is sent'
            expected_log = expected_log % {
            'contact':outbound_message.contact.value,
            'message':outbound_message.__unicode__()
            }
            

            result = send_mails_task()
            info.assert_called_with(expected_log)

    def test_it_logs_everytime_it_starts_sending_emails(self):
        with patch('logging.info') as info:
            expected_log = 'Sending messages'
            result = send_mails_task()
            info.assert_called_with(expected_log)