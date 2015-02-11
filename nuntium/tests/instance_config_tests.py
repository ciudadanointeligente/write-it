# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from nuntium.models import WriteItInstance, WriteItInstanceConfig
from popit.models import ApiInstance, Person
from django.contrib.auth.models import User


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
