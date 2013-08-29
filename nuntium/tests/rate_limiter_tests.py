# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from django.contrib.auth.models import User
from nuntium.models import WriteItInstance


class RateLimiterTestCase(TestCase):
    def setUp(self):
        super(RateLimiterTestCase, self).setUp()
        self.owner = User.objects.all()[0]

    def test_a_writeit_instance_has_a_rate_limiter_by_default_0(self):
        instance  = WriteItInstance.objects.create(name='instance 234', slug='instance-234', owner=self.owner)

        self.assertEquals(instance.rate_limiter, 0)

