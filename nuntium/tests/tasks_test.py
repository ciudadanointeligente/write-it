# coding=utf-8
from global_test_case import GlobalTestCase as TestCase, popit_load_data
from nuntium.models import OutboundMessage, WriteItInstance
from ..tasks import send_mails_task
from mock import patch
from popit.models import ApiInstance, Person
from nuntium.popit_api_instance import PopitApiInstance
from django.contrib.auth.models import User
from django.utils.unittest import skipUnless
from django.conf import settings


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

from nuntium.tasks import pull_from_popit

class PullFromPopitTask(TestCase):
    def setUp(self):
        super(PullFromPopitTask, self).setUp()
        self.api_instance1 = PopitApiInstance.objects.create(url=settings.TEST_POPIT_API_URL)
        self.person1 = Person.objects.all()[0]

        self.owner = User.objects.all()[0]

    def test_the_pulling_task_name(self):
        '''The pulling from Popit Task has a name'''
        self.assertEquals(pull_from_popit.name, 'nuntium.tasks.pull_from_popit')

    @skipUnless(settings.LOCAL_POPIT, "No local popit running")
    def test_do_the_pulling(self):
        '''Actually do the pulling from popit in an asynchronous way'''
        Person.objects.all().delete()
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)
        result = pull_from_popit.delay(writeitinstance, self.api_instance1)
        print result.result
        self.assertTrue(writeitinstance.persons.all())



    # def test_pull_from_popit_task(self):

