# coding=utf-8
from urlparse import urlsplit, urlunsplit
from global_test_case import GlobalTestCase as TestCase, popit_load_data
from subdomains.utils import reverse
from instance.models import InstanceMembership, WriteItInstance
from nuntium.models import Message, Confirmation
from popit.models import ApiInstance, Person
from django.utils.unittest import skip
from django.contrib.auth.models import User
from django.utils.translation import activate
from django.utils.translation import ugettext as _
from django.conf import settings
from mock import patch
from nuntium.popit_api_instance import PopitApiInstance
from requests.exceptions import ConnectionError
from contactos.models import Contact, ContactType


class InstanceTestCase(TestCase):
    def setUp(self):
        super(InstanceTestCase, self).setUp()
        self.api_instance1 = ApiInstance.objects.get(id=1)
        self.api_instance2 = ApiInstance.objects.get(id=2)
        self.person1 = Person.objects.get(id=1)

        self.owner = User.objects.get(id=1)

    def test_create_instance(self):
        writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.owner)
        self.assertTrue(writeitinstance.id)
        self.assertEquals(writeitinstance.name, 'instance 1')
        self.assertEquals(writeitinstance.slug, 'instance-1')
        self.assertEquals(writeitinstance.owner, self.owner)
        self.assertFalse(writeitinstance.config.notify_owner_when_new_answer)
        self.assertTrue(writeitinstance.config.autoconfirm_api_messages)

    def test_owner_related_name(self):
        writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',

            owner=self.owner)

        self.assertIn(writeitinstance, self.owner.writeitinstances.all())

    def test_instance_unicode(self):
        writeitinstance = WriteItInstance.objects.get(id=1)
        self.assertEquals(writeitinstance.__unicode__(), writeitinstance.name)

    def test_instance_containning_several_messages(self):
        writeitinstance1 = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)
        writeitinstance2 = WriteItInstance.objects.create(name='instance 2', slug='instance-2', owner=self.owner)
        message1 = Message.objects.create(content='Content 1', subject='Subject 1', writeitinstance=writeitinstance1, persons=[self.person1])
        message2 = Message.objects.create(content='Content 2', subject='Subject 2', writeitinstance=writeitinstance1, persons=[self.person1])
        message3 = Message.objects.create(content='Content 3', subject='Subject 3', writeitinstance=writeitinstance2, persons=[self.person1])
        self.assertEquals(writeitinstance1.message_set.count(), 2)
        self.assertEquals(message1.writeitinstance, writeitinstance1)
        self.assertEquals(message2.writeitinstance, writeitinstance1)
        self.assertEquals(writeitinstance2.message_set.count(), 1)
        self.assertEquals(message3.writeitinstance, writeitinstance2)

    def test_get_absolute_url(self):
        writeitinstance1 = WriteItInstance.objects.get(id=1)
        expected_url = reverse(
            'instance_detail',
            subdomain=writeitinstance1.slug,
            )

        self.assertEquals(expected_url, writeitinstance1.get_absolute_url())

    def test_get_absolute_url_i18n(self):
        activate("es")
        writeitinstance1 = WriteItInstance.objects.get(id=1)
        self.assertTrue(writeitinstance1.get_absolute_url().endswith('/es/'))
        response = self.client.get(writeitinstance1.get_absolute_url())
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'nuntium/instance_detail.html')

    def test_redirected_to_instance_default_language(self):
        writeitinstance2 = WriteItInstance.objects.get(id=2)
        url = reverse('instance_detail', subdomain=writeitinstance2.slug)
        uri = list(urlsplit(url))
        uri[2] = '/'
        url = urlunsplit(uri)
        response = self.client.get(url)
        uri[2] = '/es/'
        url = urlunsplit(uri)
        self.assertRedirects(response, url)

    def test_no_redirect_with_specified_language(self):
        writeitinstance2 = WriteItInstance.objects.get(id=2)
        url = reverse('instance_detail', subdomain=writeitinstance2.slug)
        uri = list(urlsplit(url))
        uri[2] = '/cs/'
        url = urlunsplit(uri)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_get_non_existing_instance(self):
        url = reverse('instance_detail',
            subdomain="non-existing-slug")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_membership(self):
        writeitinstance = WriteItInstance.objects.create(name=u'instance 1', slug=u'instance-1', owner=self.owner)

        InstanceMembership.objects.create(writeitinstance=writeitinstance, person=self.person1)
        self.assertEquals(writeitinstance.persons.get(id=self.person1.id), self.person1)
        self.assertEquals(self.person1.writeit_instances.get(id=writeitinstance.id), writeitinstance)

    @popit_load_data()
    def test_create_an_instance_and_load_persons_from_an_api(self):
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)

        writeitinstance.load_persons_from_a_popit_api(settings.TEST_POPIT_API_URL)

        self.assertEquals(writeitinstance.persons.all().count(), 2)

        raton = Person.objects.get(name='Ratón Inteligente')
        fiera = Person.objects.get(name="Fiera Feroz")

        self.assertIn(raton, [r for r in writeitinstance.persons.all()])
        self.assertIn(fiera, [r for r in writeitinstance.persons.all()])

    def test_it_uses_the_async_task_to_pull_people_from_popit(self):
        '''It uses the async task to pull people from popit'''
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)
        popit_api_instance, created = PopitApiInstance.objects.get_or_create(url=settings.TEST_POPIT_API_URL)

        '''
        I'm going to patch the method to know that it was run, I could do some other properties but I'm thinking that
        this is the easyest to know if the method was used.
        '''
        with patch('nuntium.tasks.pull_from_popit.delay') as async_pulling_from_popit:
            writeitinstance.load_persons_from_a_popit_api(settings.TEST_POPIT_API_URL)
            async_pulling_from_popit.assert_called_with(writeitinstance, popit_api_instance)

    @popit_load_data()
    def test_it_has_a_pulling_from_popit_status(self):
        '''It has a pulling from popit status'''
        writeitinstance = WriteItInstance.objects.create(name=u'instance 1', slug=u'instance-1', owner=self.owner)
        self.assertEquals(writeitinstance.pulling_from_popit_status, {'nothing': 0,
            'inprogress': 0,
            'success': 0,
            'error': 0})
        writeitinstance.load_persons_from_a_popit_api(settings.TEST_POPIT_API_URL)
        self.assertEquals(writeitinstance.pulling_from_popit_status,
            {
                'nothing': 0,
                'inprogress': 0,
                'success': 1,
                'error': 0
            })

        popit_api_instance, created = PopitApiInstance.objects.get_or_create(url=settings.TEST_POPIT_API_URL)

    @popit_load_data()
    def test_can_create_messages(self):
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)

        self.assertTrue(writeitinstance.config.allow_messages_using_form)
        self.assertFalse(writeitinstance.can_create_messages)
        writeitinstance.load_persons_from_a_popit_api(settings.TEST_POPIT_API_URL)

        email_type = ContactType.objects.get(id=1)
        person = Person.objects.get(id=1)
        Contact.objects.create(
            person=person,
            contact_type=email_type,
            writeitinstance=writeitinstance,
            value='email@mail.com',
            )
        self.assertEquals(writeitinstance.contacts.all().count(), 1)
        self.assertTrue(writeitinstance.can_create_messages)

        writeitinstance.config.allow_messages_using_form = False
        self.assertFalse(writeitinstance.config.allow_messages_using_form)
        self.assertFalse(writeitinstance.can_create_messages)


class PersonsWithContactsTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.get(id=1)
        super(PersonsWithContactsTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.owner)
        self.person1 = Person.objects.get(id=1)
        self.person2 = Person.objects.get(id=2)

    def test_instance_add_person(self):
        self.writeitinstance.add_person(self.person1)
        self.assertIn(self.person1, self.writeitinstance.persons.all())

    def test_writeitinstance_people_with_contacts(self):
        '''A ẂriteitInstance has a property that returns only the persons with contacts'''
        email_type = ContactType.objects.get(id=1)
        Contact.objects.create(
            person=self.person2,
            contact_type=email_type,
            writeitinstance=self.writeitinstance,
            value='email@mail.com',
            )
        Contact.objects.create(
            person=self.person2,
            contact_type=email_type,
            writeitinstance=self.writeitinstance,
            value='email2@mail.com',
            )
        # self.person1 does not have contacts
        # self.person2 has contacts
        self.writeitinstance.add_person(self.person1)
        self.writeitinstance.add_person(self.person2)

        self.assertNotIn(self.person1,
            self.writeitinstance.persons_with_contacts)
        self.assertIn(self.person2,
            self.writeitinstance.persons_with_contacts)

        self.assertEquals(self.writeitinstance.persons_with_contacts.count(), 1)


class WriteItInstanceLoadingPeopleFromAPopitApiTestCase(TestCase):
    def setUp(self):
        super(WriteItInstanceLoadingPeopleFromAPopitApiTestCase, self).setUp()
        self.api_instance1 = ApiInstance.objects.get(id=1)
        self.api_instance2 = ApiInstance.objects.get(id=2)
        self.person1 = Person.objects.get(id=1)

        self.owner = User.objects.get(id=1)

    @popit_load_data()
    def test_load_persons_from_a_popit_api(self):
        '''Loading persons from a popit api'''
        popit_api_instance, created = PopitApiInstance.objects.get_or_create(url=settings.TEST_POPIT_API_URL)
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)
        writeitinstance.relate_with_persons_from_popit_api_instance(popit_api_instance)

        self.assertEquals(writeitinstance.persons.all().count(), 2)

        raton = Person.objects.get(name='Ratón Inteligente')
        fiera = Person.objects.get(name="Fiera Feroz")

        self.assertIn(raton, [r for r in writeitinstance.persons.all()])
        self.assertIn(fiera, [r for r in writeitinstance.persons.all()])

    @popit_load_data()
    def test_it_returns_a_tuple(self):
        '''Returns a tuple'''
        popit_api_instance, created = PopitApiInstance.objects.get_or_create(url=settings.TEST_POPIT_API_URL)
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)
        result = writeitinstance.relate_with_persons_from_popit_api_instance(popit_api_instance)
        self.assertIsInstance(result, tuple)
        self.assertTrue(result[0])
        self.assertIsNone(result[1])

    def test_it_returns_false_when_theres_a_problem(self):
        '''When there's a problem it returns false and the problem in the tuple'''
        non_existing_url = "http://nonexisting.url"
        popit_api_instance = PopitApiInstance.objects.create(url=non_existing_url)
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)
        result = writeitinstance.relate_with_persons_from_popit_api_instance(popit_api_instance)
        self.assertIsInstance(result, tuple)
        self.assertFalse(result[0])
        self.assertIsInstance(result[1], ConnectionError)


class InstanceDetailView(TestCase):
    def setUp(self):
        super(InstanceDetailView, self).setUp()
        self.api_instance1 = ApiInstance.objects.get(id=1)
        self.api_instance2 = ApiInstance.objects.get(id=2)
        self.person1 = Person.objects.get(id=1)
        self.writeitinstance1 = WriteItInstance.objects.get(id=1)
        self.url = self.writeitinstance1.get_absolute_url()

    def test_detail_instance_view(self):
        #I'm removing this because it has been already tested
        #self.assertTrue(url)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'nuntium/instance_detail.html')
        self.assertEquals(response.context['writeitinstance'], self.writeitinstance1)
        self.assertEquals(response.status_code, 200)

    def test_list_only_public_messages(self):
        private_message = Message.objects.create(
            content='Content 1',
            subject='a private message',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            public=False,
            )
        response = self.client.get(self.url)

        self.assertTrue('recent_messages' in response.context)
        self.assertTrue(private_message not in response.context['recent_messages'])

    def test_in_moderation_needed_instances_does_not_show_a_confirmated_but_not_moderated(self):
        self.writeitinstance1.config.moderation_needed_in_all_messages = True

        self.writeitinstance1.config.save()
        message = Message.objects.create(
            content='Content 3',
            subject='Subject 3',
            writeitinstance=self.writeitinstance1,
            confirmated=True,
            persons=[self.person1],
            )

        confirmation = Confirmation.objects.create(message=message)
        self.client.get(confirmation.get_absolute_url())

        # ok it is now confirmated but it is not moderated

        url = self.writeitinstance1.get_absolute_url()
        response = self.client.get(url)

        self.assertNotIn(message, response.context['recent_messages'])

    def test_list_only_confirmed_and_public_messages(self):
        message1 = self.writeitinstance1.message_set.all()[0]
        message2 = self.writeitinstance1.message_set.all()[1]
        message3 = Message.objects.create(
            content='Content 3',
            subject='Subject 3',
            writeitinstance=self.writeitinstance1,
            confirmated=True,
            persons=[self.person1],
            )
        private_message = Message.objects.create(
            content='Content 1',
            subject='a private message',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            confirmated=True,
            public=False,
            )

        confirmation_for_message2 = Confirmation.objects.create(message=message2)
        self.client.get(confirmation_for_message2.get_absolute_url())

        # now I need to moderate this
        self.client.get(private_message.moderation.get_success_url())

        confirmation_for_private_message = Confirmation.objects.create(message=private_message)
        self.client.get(reverse('confirm',
            subdomain=private_message.writeitinstance.slug,
            kwargs={'slug': confirmation_for_private_message.key}))

        url = self.writeitinstance1.get_absolute_url()
        response = self.client.get(url)

        # message1 is not confirmed so it should not be in the list
        # private_message is not in the list either
        # only message 2 is in the list because is public and confirmed

        self.assertIn(message2, response.context['recent_messages'])
        self.assertNotIn(message1, response.context['recent_messages'])
        self.assertIn(message3, response.context['recent_messages'])
        self.assertNotIn(private_message, response.context["recent_messages"])

    @skip('Message creation is no longer in the instance detail view')
    def test_message_creation_on_post_form(self):
        # Spanish
        data = {
            'author_email': u'falvarez@votainteligente.cl',
            'author_name': u'feli',
            'subject': u'Fiera no está',
            'content': u'¿Dónde está Fiera Feroz? en la playa?',
            'persons': [self.person1.id],
            }
        response = self.client.post(self.url, data, follow=True)
        self.assertEquals(response.status_code, 200)
        new_messages = Message.objects.filter(subject='Fiera no está')
        self.assertTrue(new_messages.count() > 0)
        self.assertEquals(len(response.context["form"].errors), 0)

    @skip('Message creation is no longer in the instance detail view')
    def test_I_get_an_acknoledgement_for_creating_a_message(self):
        # Spanish
        data = {
            'subject': u'Fiera no está',
            'author_email': u'falvarez@votainteligente.cl',
            'author_name': u'feli',
            'public': True,
            'content': u'¿Dónde está Fiera Feroz? en la playa?',
            'persons': [self.person1.id],
        }

        response = self.client.post(self.url, data, follow=True)
        self.assertEquals(response.status_code, 200)
        expected_acknoledgments = _("Thanks for submitting your message, please check your email and click on the confirmation link")

        self.assertContains(response, expected_acknoledgments)

        all_messages, all_retrieved = response.context["messages"]._get()

        self.assertEquals(len(all_messages), 1)
        self.assertEquals(all_messages[0].__str__(), expected_acknoledgments)

    @skip('Message creation is no longer in the instance detail view')
    def test_after_the_creation_of_a_message_it_redirects(self):
        data = {
            'subject': u'Fiera no está',
            'content': u'¿Dónde está Fiera Feroz? en la playa?',
            'author_name': u"Felipe",
            'author_email': u"falvarez@votainteligente.cl",
            'persons': [self.person1.id],
            }
        url = self.writeitinstance1.get_absolute_url()
        response = self.client.post(self.url, data)

        self.assertRedirects(response, url)

    @skip('Message creation is no longer in the instance detail view')
    def test_if_the_instance_needs_moderation_in_all_messages(self):
        self.writeitinstance1.config.moderation_needed_in_all_messages = True
        self.writeitinstance1.config.save()
        data = {
            'subject': u'Fiera no está',
            'content': u'¿Dónde está Fiera Feroz? en la playa?',
            'author_name': u"Felipe",
            'public': True,
            'author_email': u"falvarez@votainteligente.cl",
            'persons': [self.person1.id]
        }

        url = self.writeitinstance1.get_absolute_url()
        response = self.client.post(url, data, follow=True)

        expected_acknoledgments = _("Thanks for submitting your message, please check your email and click on the confirmation link, after that your message will be waiting form moderation")

        self.assertContains(response, expected_acknoledgments)

    def test_no_form_on_homepage_of_empty_instance(self):
        owner = User.objects.create(
            username='test-instance-owner',
            password='foo',
            )
        instance = WriteItInstance.objects.create(
            name="Instance Without Contacts",
            owner=owner,
            )

        url = instance.get_absolute_url()
        response = self.client.get(url)

        self.assertIn('There is no-one to write to yet', response.content)
