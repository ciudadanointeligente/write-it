# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from django.contrib.auth.models import User
from instance.models import WriteItInstance
from ..models import RateLimiter, Message
from datetime import date
from django.core.exceptions import ValidationError
from popolo.models import Person
from django.utils.translation import ugettext as _


class RateLimiterTestCase(TestCase):
    def setUp(self):
        super(RateLimiterTestCase, self).setUp()
        self.owner = User.objects.get(id=1)
        self.writeitinstance1 = WriteItInstance.objects.get(id=1)
        self.person1 = Person.objects.get(id=1)
        self.person2 = Person.objects.get(id=2)

    def test_a_writeit_instance_has_a_rate_limiter_by_default_0(self):
        instance = WriteItInstance.objects.create(name='instance 234', slug='instance-234', owner=self.owner)

        self.assertEquals(instance.config.rate_limiter, 0)

    def test_create_a_rate_limiter_instance(self):
        rate_limiter = RateLimiter.objects.create(writeitinstance=self.writeitinstance1, email='falvarez@ciudadanointeligente.org')

        self.assertTrue(rate_limiter)
        self.assertEquals(rate_limiter.writeitinstance, self.writeitinstance1)
        self.assertEquals(rate_limiter.day, date.today())
        self.assertEquals(rate_limiter.email, 'falvarez@ciudadanointeligente.org')
        self.assertEquals(rate_limiter.count, 1)

    def test_every_time_a_user_creates_a_message_it_adds_a_rate_limiter(self):
        message1 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="fieramolestando@votainteligente.cl",
            confirmated=True,
            subject='Test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        self.assertEquals(RateLimiter.objects.filter(email=message1.author_email).count(), 1)
        rate_limiter = RateLimiter.objects.get(email=message1.author_email)

        self.assertEquals(rate_limiter.day, date.today())
        self.assertEquals(rate_limiter.email, message1.author_email)
        self.assertEquals(rate_limiter.count, 1)

    def test_if_the_message_does_not_have_email_author_it_does_not_create_one(self):
        message1 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            confirmated=True,
            subject='Test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        self.assertEquals(RateLimiter.objects.filter(email=message1.author_email).count(), 0)

    def test_the_second_message_increments_the_counter(self):
        message1 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="fieramolestando@votainteligente.cl",
            confirmated=True,
            subject='Test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        # the second message increments the counter

        message1 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="fieramolestando@votainteligente.cl",
            confirmated=True,
            subject='Test2',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        rate_limiter = RateLimiter.objects.get(email=message1.author_email)
        self.assertEquals(rate_limiter.count, 2)

    def test_the_counter_restarts_every_day(self):
        some_other_day = date(2013, 8, 29)  # that was acctually yesterday
        message1 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="fieramolestando@votainteligente.cl",
            confirmated=True,
            subject='Test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        rate_limiter = RateLimiter.objects.get(email=message1.author_email)
        rate_limiter.day = some_other_day
        rate_limiter.save()
        # ok at this point there should be a rate_limiter for yesterday but not for today

        message1 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="fieramolestando@votainteligente.cl",
            confirmated=True,
            subject='Test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        rate_limiter_for_some_other_day = RateLimiter.objects.get(email=message1.author_email, day=some_other_day)
        self.assertEquals(rate_limiter_for_some_other_day.count, 1)

        rate_limiter_for_today = RateLimiter.objects.get(email=message1.author_email, day=date.today())
        self.assertEquals(rate_limiter_for_today.count, 1)

    def test_maximum_rate_exceded(self):
        self.writeitinstance1.config.rate_limiter = 1
        self.writeitinstance1.config.save()

        Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="fieramolestando@votainteligente.cl",
            confirmated=True,
            subject='Test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        message2 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="fieramolestando@votainteligente.cl",
            confirmated=True,
            subject='Test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        with self.assertRaises(ValidationError) as error:
            message2.clean()

        self.assertEquals(error.exception.messages[0], _('You have reached your limit for today please try again tomorrow'))

    def test_when_a_message_is_created_and_rate_limiter_is_zero_it_does_not_raise_anything(self):
        message1 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="fieramolestando@votainteligente.cl",
            confirmated=True,
            subject='Test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        try:
            message1.clean()
        except:  # pragma: no cover
            self.fail("It didn't pass the clean when it whould have")
