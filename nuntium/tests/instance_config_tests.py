# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from nuntium.models import WriteItInstance, WriteItInstanceConfig, \
    Message, Membership
from popit.models import ApiInstance, Person
from django.contrib.auth.models import User
from mailit import MailChannel
from contactos.models import Contact
from django.core import mail


class WriteItInstanceConfigTestCase(TestCase):
    def setUp(self):
        super(WriteItInstanceConfigTestCase, self).setUp()
        self.api_instance1 = ApiInstance.objects.all()[0]
        self.api_instance2 = ApiInstance.objects.all()[1]
        self.person1 = Person.objects.all()[0]

        self.owner = User.objects.all()[0]

        self.writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.owner)

    def test_instanciate_and_have_properties(self):
        config = WriteItInstanceConfig.objects.create(
            writeitinstance=self.writeitinstance
            )
        self.assertTrue(config)
        self.assertTrue(config.testing_mode)

    def test_a_writeitinstance_has_a_config_model(self):
        '''A WriteItInstance has a config'''
        self.assertTrue(self.writeitinstance.config)
        self.assertIsInstance(self.writeitinstance.config, WriteItInstanceConfig)


class TestingModeTestCase(TestCase):
    def setUp(self):
        super(TestingModeTestCase, self).setUp()
        self.person1 = Person.objects.all()[0]

        self.owner = User.objects.all()[0]
        self.owner.email = "owner@ciudadanoi.org"
        self.owner.save()

        self.writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.owner)
        Membership.objects.create(writeitinstance=self.writeitinstance, person=self.person1)

        self.channel = MailChannel()
        self.contact = Contact.objects.create(
            person=self.person1,
            contact_type=self.channel.get_contact_type(),
            value='person1@votainteligente.cl',
            writeitinstance=self.writeitinstance,
            )
        self.message = Message.objects.create(
            content="The content",
            subject="the subject",
            writeitinstance=self.writeitinstance,
            persons=[self.person1],
            author_name="Felipe",
            author_email="falvarez@votainteligente.cl",
            )

    def test_testing_mode_send_mail(self):
        '''When testing mode is on the messages are sent to the owner's email'''
        outbound_message = self.message.outboundmessage_set.all()[0]

        self.writeitinstance.config.testing_mode = True
        self.writeitinstance.config.save()

        self.channel.send(outbound_message)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertIn(self.owner.email, mail.outbox[0].to)
