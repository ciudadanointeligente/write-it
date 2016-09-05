# coding=utf-8
from django.test import TestCase as OriginalTestCase
from global_test_case import GlobalTestCase as TestCase
from global_test_case import UsingDbMixin
from django.db import IntegrityError
from django.utils.translation import ugettext as _
from contactos.models import Contact
from instance.models import WriteItInstance
from ..models import Message, OutboundMessage, NoContactOM
from popolo.models import Person
from subdomains.utils import reverse
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import datetime
from django.db.models.query import QuerySet


class TestMessages(TestCase):
    def setUp(self):
        super(TestMessages, self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.get(id=1)
        self.person1 = Person.objects.get(id=1)
        self.person2 = Person.objects.get(id=2)

    def test_create_message(self):
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Fiera es una perra feroz',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        self.assertTrue(message)
        self.assertEquals(message.content, "Content 1")
        self.assertEquals(message.subject, "Fiera es una perra feroz")
        self.assertEquals(message.writeitinstance, self.writeitinstance1)
        self.assertEquals(message.slug, slugify(message.subject))
        self.assertFalse(message.confirmated)
        self.assertTrue(message.public)

        self.assertIsNone(message.moderated)

        self.assertIsNotNone(message.created)
        self.assertIsNotNone(message.updated)
        self.assertIsInstance(message.created, datetime.datetime)
        self.assertIsInstance(message.updated, datetime.datetime)

    def test_message_has_a_is_confirmated_field(self):
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            confirmated=True,
            subject='Fiera es una perra feroz',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        self.assertTrue(message.confirmated)

    # This intended to fix this bug
    # https://github.com/ciudadanointeligente/write-it/issues/167
    def test_two_messages_with_the_same_slug_throw_an_error(self):
        Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            confirmated=True,
            subject='test',
            slug='test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        message2 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            confirmated=True,
            subject='test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        message2.slug = 'test'
        with self.assertRaises(IntegrityError):
            message2.save()

    def test_two_messages_with_different_capital_letters(self):
        message1 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            confirmated=True,
            subject='Test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        message2 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            confirmated=True,
            subject='test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        self.assertNotEqual(message1.slug, message2.slug)

    def test_create_a_message_with_a_non_sluggable_subject(self):
        message1 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            confirmated=True,
            subject=':)',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        message1.save()

        self.assertGreater(len(message1.slug), 0)

    def test_four_messaes_with_the_same_slug(self):
        message1 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            confirmated=True,
            subject='Test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        message2 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            confirmated=True,
            subject='Test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        message3 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            confirmated=True,
            subject='Test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        message4 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            confirmated=True,
            subject='Test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        self.assertEquals(message1.slug, 'test')
        self.assertEquals(message2.slug, 'test-2')
        self.assertEquals(message3.slug, 'test-3')
        self.assertEquals(message4.slug, 'test-4')

    def test_update_a_message_does_not_need_persons(self):
        message1 = Message.objects.get(id=1)

        previous_people = message1.people

        message1.slug = 'a-new-slug1'

        message1.save()
        self.assertQuerysetEqual(
            message1.people.all(),
            [repr(r) for r in previous_people],
            ordered=False,
            )

    def test_message_has_a_permalink(self):
        message1 = Message.objects.get(id=1)
        expected_url = reverse('thread_read', subdomain=message1.writeitinstance.slug, kwargs={'slug': message1.slug})

        self.assertEquals(expected_url, message1.get_absolute_url())

    def test_message_set_to_ready(self):
        message1 = Message.objects.get(id=1)

        message1.set_to_ready()
        first_om = OutboundMessage.objects.filter(message=message1)[0]
        second_om = OutboundMessage.objects.filter(message=message1)[1]

        self.assertEquals(first_om.status, 'ready')
        self.assertEquals(second_om.status, 'ready')

    def test_two_messages_with_the_same_subject_but_different_slug(self):
        message1 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Same subject hey',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        message2 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Same subject hey',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        message3 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Same subject hey',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        self.assertEquals(message1.slug, slugify(message1.subject))
        self.assertEquals(message2.slug, slugify(message2.subject) + "-2")
        self.assertEquals(message3.slug, slugify(message3.subject) + "-3")

    def test_a_person_with_two_contacts_method_people(self):
        '''A message.people() returns the people to which the message was sent based on the contacts'''
        Contact.objects.create(
            person=self.person1,
            value=u"another@contact.cl",
            contact_type=self.person1.contact_set.all()[0].contact_type,
            writeitinstance=self.writeitinstance1,
            )

        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Same subject hey',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        self.assertIn(self.person1, message.people.all())
        self.assertEquals(message.people.count(), 1)

    def test_resave_a_message_should_not_change_slug(self):
        # There are a lot of good solutions for this problem but this
        # is the easyest one
        message1 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Same subject hey',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        previous_slug = message1.slug
        # message1 now has a slug
        message1.subject = 'Some other subject and stuff'
        message1.save()

        self.assertEquals(message1.slug, previous_slug)

    def test_a_message_has_a_people_property(self):
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Same subject hey',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1, self.person2],
            )

        self.assertIsInstance(message.people, QuerySet)
        self.assertIn(self.person1, message.people.all())
        self.assertIn(self.person2, message.people.all())
        self.assertEquals(message.people.count(), 2)

    def test_a_person_has_a_messages_property(self):
        Message.objects.all().delete()
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Same subject hey',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        messages_to_person1 = Message.objects.filter(person=self.person1)
        messages_to_person2 = Message.objects.filter(person=self.person2)

        self.assertIn(message, messages_to_person1)
        self.assertNotIn(message, messages_to_person2)

        self.assertEqual(len(messages_to_person1), 1)
        self.assertEqual(len(messages_to_person2), 0)

    def test_message_unicode(self):
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Subject 1',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        self.assertEquals(
            message.__unicode__(),
            _('%(subject)s at %(instance)s') % {
                'subject': message.subject,
                'instance': self.writeitinstance1.name,
                })

    def test_outboundmessage_create_without_manager(self):
        message = Message(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Subject 1',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        message.save()

        self.assertEquals(message.outboundmessage_set.count(), 1)

    def test_outbound_message_is_not_created_if_the_persons_contact_is_bounced(self):
        contact = Contact.objects.get(person=self.person1)
        contact.is_bounced = True
        contact.save()
        message = Message(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Subject 1',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        message.save()

        self.assertEquals(message.outboundmessage_set.count(), 0)

    def test_outbound_message_is_not_created_if_the_contact_is_related_to_another_instance(self):
        '''Send messages only to the contact related to its writeitinstance'''
        another_instance = WriteItInstance.objects.create(
            name=u"Another instance",
            slug=u'another-instance',
            owner=self.writeitinstance1.owner
            )
        contact = Contact.objects.create(
            person=self.person1,
            value=u"another@contact.cl",
            contact_type=self.person1.contact_set.all()[0].contact_type,
            writeitinstance=another_instance,
            )

        # this contact is for person 1 but it is owned by felipe
        Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Subject 1',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        # there should not be any outboundmessages to contact because the message was
        # sent to writeitinstance1 that is owned by felipe

        self.assertEquals(OutboundMessage.objects.filter(contact=contact).count(), 0)

    def test_it_creates_outbound_messages_only_once(self):
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Subject 1',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        message.save()

        self.assertEquals(OutboundMessage.objects.filter(message=message).count(), 1)

    def test_it_raises_typeerror_when_no_contacts_are_present(self):
        with self.assertRaises(TypeError):
            Message.objects.create(
                content='Content 1',
                author_name='Felipe',
                author_email="falvarez@votainteligente.cl",
                subject='Subject 1',
                writeitinstance=self.writeitinstance1,
                )

    def test_message_set_new_outbound_messages_to_ready(self):
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Subject 1',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        message.recently_confirmated()

        outbound_message_to_pedro = OutboundMessage.objects.filter(message=message)[0]
        self.assertEquals(outbound_message_to_pedro.status, 'ready')
        self.assertTrue(message.confirmated)

    def test_outbound_messages_include_no_contact_and_with_contact(self):
        self.person1.contact_set.all().delete()

        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Subject 1',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1, self.person2],
            )
        no_contact_om = NoContactOM.objects.get(person=self.person1, message=message)
        outbound_message = OutboundMessage.objects.get(message=message)

        self.assertTrue(message.outbound_messages)

        self.assertIn(no_contact_om, message.outbound_messages)
        self.assertIn(outbound_message, message.outbound_messages)

    def test_message_ordering(self):
        '''Messages come ordered according to their creation date(last to first)'''
        message1 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            confirmated=True,
            subject='test1',
            slug='test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        message2 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            confirmated=True,
            subject='test2',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        messages = Message.objects.filter(id__in=[message1.id, message2.id])
        self.assertEquals(messages[0], message2)
        self.assertEquals(messages[1], message1)


class MysqlTesting(UsingDbMixin, OriginalTestCase):
    using_db = 'mysql'

    def setUp(self):
        super(MysqlTesting, self).setUp()
        user = User.objects.create_user(username='admin', password='a')
        popit_instance = ApiInstance.objects.create(
            url='http://popit.ciudadanointeligente.org',
            )

        self.writeitinstance1 = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=user,
            )
        self.person1 = Person.objects.create(name='Pedro', api_instance=popit_instance)

    # This test was a bug against mysql
    def test_a_message_with_a_changed_slug(self):
        message1 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            confirmated=True,
            subject='Test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        message1.slug = 'test-2'
        message1.save()

        # regex = "^" + message1.slug + "(-\d+){0,1}$"
        # previously = Message.objects.filter(slug__regex=regex).count()

        message2 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            confirmated=True,
            subject='test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        self.assertEquals(message2.slug, 'test-3')

    def test_a_message_with_a_RTL_language(self):
        content = u"رسمية هي اللغة العربية، وهي جزء من المغرب العربي الكبير. وبصفتها"
        subject = u"مواصلة العمل للمحافظة على السلام والأمن"
        message1 = Message.objects.create(
            content=content,
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            confirmated=True,
            subject=subject,
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        self.assertEquals(message1.content, content)
        self.assertEquals(message1.subject, subject)


class PostgresTesting(UsingDbMixin, OriginalTestCase):
    using_db = 'postgres'

    def setUp(self):
        super(PostgresTesting, self).setUp()
        user = User.objects.create_user(username='admin', password='a')
        popit_instance = ApiInstance.objects.create(
            url='http://popit.ciudadanointeligente.org',
            )

        self.writeitinstance1 = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=user)
        self.person1 = Person.objects.create(name='Pedro', api_instance=popit_instance)

    # This test was a bug against mysql
    def test_a_message_with_a_changed_slug(self):
        message1 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            confirmated=True,
            subject='Test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        message1.slug = 'test-2'
        message1.save()

        # regex = "^" + message1.slug + "(-\d+){0,1}$"
        # previously = Message.objects.filter(slug__regex=regex).count()

        message2 = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            confirmated=True,
            subject='test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        self.assertEquals(message2.slug, 'test-3')

    def test_a_message_with_a_RTL_language(self):
        content = u"رسمية هي اللغة العربية، وهي جزء من المغرب العربي الكبير. وبصفتها"
        subject = u"مواصلة العمل للمحافظة على السلام والأمن"
        message1 = Message.objects.create(
            content=content,
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            confirmated=True,
            subject=subject,
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        self.assertEquals(message1.content, content)
        self.assertEquals(message1.subject, subject)
