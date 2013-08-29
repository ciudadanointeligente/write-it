# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from django.contrib.auth.models import User
from nuntium.models import WriteItInstance, RateLimiter
from datetime import date
from popit.models import Person

class RateLimiterTestCase(TestCase):
    def setUp(self):
        super(RateLimiterTestCase, self).setUp()
        self.owner = User.objects.all()[0]
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.person1 = Person.objects.all()[0]
        self.person2 = Person.objects.all()[1]

    def test_a_writeit_instance_has_a_rate_limiter_by_default_0(self):
        instance  = WriteItInstance.objects.create(name='instance 234', slug='instance-234', owner=self.owner)

        self.assertEquals(instance.rate_limiter, 0)

    def test_create_a_rate_limiter_instance(self):
        rate_limiter = RateLimiter.objects.create(writeitinstance=self.writeitinstance1, email='falvarez@ciudadanointeligente.org')

        self.assertTrue(rate_limiter)
        self.assertEquals(rate_limiter.writeitinstance, self.writeitinstance1)
        self.assertEquals(rate_limiter.day, date.today())
        self.assertEquals(rate_limiter.email, 'falvarez@ciudadanointeligente.org')
