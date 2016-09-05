# coding=utf-8
from global_test_case import GlobalTestCase as TestCase, popit_load_data
from instance.models import WriteItInstance, WriteitInstancePopitInstanceRecord
from nuntium.models import OutboundMessage
from ..tasks import send_mails_task
from mock import patch
from popolo.models import Person
from django.contrib.auth.models import User
from django.conf import settings
from nuntium.tasks import pull_from_popit, update_all_popits


class TasksTestCase(TestCase):
    def setUp(self):
        super(TasksTestCase, self).setUp()

    def test_it_has_a_name(self):
        self.assertEquals(send_mails_task.name, 'nuntium.tasks.send_mails_task')

    def test_it_sends_the_emails(self):
        for outbound_message in OutboundMessage.objects.all():
            outbound_message.status = "ready"
            outbound_message.save()

        send_mails_task()

        self.assertEquals(OutboundMessage.objects.filter(status="new").count(), 0)
        self.assertEquals(
            OutboundMessage.objects.filter(status="sent").count(),
            OutboundMessage.objects.count(),
            )

    def test_it_logs_the_sending_of_emails(self):
        outbound_message = OutboundMessage.objects.get(id=1)
        outbound_message.status = 'ready'
        outbound_message.save()

        with patch('logging.info') as info:
            info.return_value = None

            expected_log = 'Sending "%(message)s" to %(contact)s and the result is sent'
            expected_log = expected_log % {
                'contact': outbound_message.contact.value,
                'message': outbound_message.__unicode__(),
                }

            send_mails_task()
            info.assert_called_with(expected_log)

    def test_it_logs_everytime_it_starts_sending_emails(self):
        with patch('logging.info') as info:
            expected_log = 'Sending messages'
            send_mails_task()  # It returns a result
            info.assert_called_with(expected_log)

    def test_handling_unexpected_exceptions_in_send(self):
        for outbound_message in OutboundMessage.objects.all():
            outbound_message.status = "ready"
            outbound_message.save()

        instance = WriteItInstance.objects.get(id=1)
        instance.mailit_template.content_template = '{autor}'
        instance.mailit_template.save()

        send_mails_task()

        other_instance = WriteItInstance.objects.get(id=2)
        self.assertTrue(OutboundMessage.objects.filter(message__writeitinstance=other_instance, status="sent"))


class PullFromPopitTask(TestCase):
    def setUp(self):
        super(PullFromPopitTask, self).setUp()
        self.api_instance1 = PopitApiInstance.objects.create(url=settings.TEST_POPIT_API_URL)
        self.person1 = Person.objects.get(id=1)

        self.owner = User.objects.get(id=1)

    def test_the_pulling_task_name(self):
        '''The pulling from Popit Task has a name'''
        self.assertEquals(pull_from_popit.name, 'nuntium.tasks.pull_from_popit')

    @popit_load_data()
    def test_do_the_pulling(self):
        '''Actually do the pulling from popit in an asynchronous way'''
        Person.objects.all().delete()
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)
        WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=writeitinstance,
            popitapiinstance=self.api_instance1
            )
        pull_from_popit.delay(writeitinstance, self.api_instance1)  # Returns result
        self.assertTrue(writeitinstance.persons.all())


class PeriodicallyPullFromPopitClass(TestCase):
    def setUp(self):
        super(PeriodicallyPullFromPopitClass, self).setUp()
        self.owner = User.objects.get(id=1)
        #this is the popit_api_instance created based on the previous load
        self.writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)

        self.popit_api_instance, created = PopitApiInstance.objects.get_or_create(url=settings.TEST_POPIT_API_URL)
        WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=self.writeitinstance,
            popitapiinstance=self.popit_api_instance
            )
        #loading data from popit in a sync way
        with popit_load_data():
            self.writeitinstance._load_persons_from_a_popit_api(self.popit_api_instance)
        self.previously_created_persons = list(self.writeitinstance.persons.all())

    @popit_load_data("other_persons")
    def test_update_existing(self):
        '''Update existing instance with new information coming from popit'''

        # This means that if I run the task then it should update the persons
        # I'm running the weekly job by default
        update_all_popits.delay()

        persons_after_updating = list(self.writeitinstance.persons.all())
        self.assertNotEquals(self.previously_created_persons, persons_after_updating)

    @popit_load_data("other_persons")
    def test_it_does_not_autosync_if_disabled(self):
        '''If the instance has autosync disabled then it does not sync'''
        writeitinstance_popit_record = WriteitInstancePopitInstanceRecord.objects.get(
            writeitinstance=self.writeitinstance,
            popitapiinstance=self.popit_api_instance
        )
        # Periodicity = 0  means that it is never going to send anything
        writeitinstance_popit_record.periodicity = 0
        writeitinstance_popit_record.save()

        # The record has been set to autosync False
        update_all_popits.delay()
        # Loading new data
        persons_after_updating = list(self.writeitinstance.persons.all())
        # It should not have updated our writeit instance
        self.assertEquals(self.previously_created_persons, persons_after_updating)

    @popit_load_data("other_persons")
    def test_autosyncs_receiving_a_parameter_with_the_periodicity(self):
        '''It can receive a parameter refering to the periodicity'''
        writeitinstance_popit_record = WriteitInstancePopitInstanceRecord.objects.get(
            writeitinstance=self.writeitinstance,
            popitapiinstance=self.popit_api_instance
        )
        writeitinstance_popit_record.periodicity = '1D'  # Daily
        writeitinstance_popit_record.save()

        # Now because it is receiving the default value = '1W'
        # it should not pull anyone
        update_all_popits.delay()

        persons_after_updating = list(self.writeitinstance.persons.all())
        self.assertEquals(self.previously_created_persons, persons_after_updating)

        # But If I tell the runner that I'm running the daily
        # process then it should change it
        update_all_popits.delay(periodicity="1D")
        persons_after_updating = list(self.writeitinstance.persons.all())
        self.assertNotEquals(self.previously_created_persons, persons_after_updating)
