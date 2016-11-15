# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from instance.models import WriteItInstance
from nuntium.models import Message
from popolo.models import Person
from subdomains.utils import reverse
from django.utils.unittest import skip

class SeeAllMessagesFromAPersonTestCase(TestCase):
    def setUp(self):
        super(SeeAllMessagesFromAPersonTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.get(id=1)
        # Fiera is the author for this message
        # and this is the only message that should be displayed
        # as it is public and is confirmed
        self.message = Message.objects.get(id=2)

        self.not_a_fieras_message = Message.objects.create(subject=u"A message",
            content="that should not be in the list because it was sent from",
            author_name="Felipe not Fiera",
            author_email="falvarez@votainteligente.cl",
            writeitinstance=self.writeitinstance,
            persons=list(self.message.people))
        self.not_a_fieras_message.recently_confirmated()

    def test_get_all_messages_from_a_person_view(self):
        '''There is a view that displays all messages written by that person'''
        url = reverse('all-messages-from-the-same-author-as', subdomain=self.message.writeitinstance.slug,
            kwargs={
                'message_slug': self.message.slug
            })

        # According to the fixture data Fiera (fiera@ciudadanointeligente.org)
        # has sent 3 messages.
        # 1 is public and confirmed (id=2)
        # 1 is public but not confirmed (id=1)
        # 1 is public (id=3)

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('message_list', response.context)
        self.assertEquals(len(response.context['message_list']), 1)
        # I'm expecting only the message that is public and confirmed
        # to be in this list
        self.assertEquals(response.context['message_list'][0].id, 2)
        self.assertIn('author_name', response.context)
        self.assertEquals(response.context['author_name'], self.message.author_name)

    def test_anonymous_messages_not_listed_from_non_anonymous_link(self):
        self.anonymous_message = Message.objects.create(subject=u"A message",
            content="that should not be in the list because it is anonymous",
            author_name="",
            author_email="fiera@ciudadanointeligente.org",
            writeitinstance=self.writeitinstance,
            persons=list(self.message.people))
        self.anonymous_message.recently_confirmated()

        url = reverse('all-messages-from-the-same-author-as', subdomain=self.message.writeitinstance.slug,
            kwargs={
                'message_slug': self.message.slug
            })

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('message_list', response.context)
        self.assertEquals(len(response.context['message_list']), 1)
        self.assertEquals(response.context['message_list'][0].id, 2)
        self.assertNotIn('because it is anonymous', response.content)

    @skip("we don't allow links to all authors for anonymous messages")
    def test_non_anonymous_messages_not_listed_from_anonymous_link(self):
        self.anonymous_message = Message.objects.create(subject=u"A message",
            content="that should not be in the list because it is anonymous",
            author_name="",
            author_email="fiera@ciudadanointeligente.org",
            writeitinstance=self.writeitinstance,
            persons=list(self.message.people))
        self.anonymous_message.recently_confirmated()

        url = reverse('all-messages-from-the-same-author-as', subdomain=self.message.writeitinstance.slug,
            kwargs={
                'message_slug': self.anonymous_message.slug
            })

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('message_list', response.context)
        self.assertEquals(len(response.context['message_list']), 1)
        self.assertEquals(response.context['message_list'][0].id, self.anonymous_message.id)
        self.assertIn('because it is anonymous', response.content)
        self.assertNotIn('Content 1', response.content)

    def test_anonymous_messages_are_404(self):
        self.anonymous_message = Message.objects.create(subject=u"A message",
            content="that should not be in the list because it is anonymous",
            author_name="",
            author_email="fiera@ciudadanointeligente.org",
            writeitinstance=self.writeitinstance,
            persons=list(self.message.people))
        self.anonymous_message.recently_confirmated()

        url = reverse('all-messages-from-the-same-author-as', subdomain=self.message.writeitinstance.slug,
            kwargs={
                'message_slug': self.anonymous_message.slug
            })

        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get_messages_404(self):
        '''Gets a 404 if the slug of an instance does not exist'''
        url = reverse('all-messages-from-the-same-author-as', subdomain='non-existing', kwargs={
            'message_slug': self.message.slug,  # This slug does not exists
            })
        self.assertEquals(self.client.get(url).status_code, 404)

    def test_get_message_slug_404(self):
        '''Gets a 404 if the slug of the message does not exists'''
        url = reverse('all-messages-from-the-same-author-as', subdomain=self.writeitinstance.slug, kwargs={
            'message_slug': 'i-am-a-slug-and-i-do-not-exist',  # This is the problem
            })
        self.assertEquals(self.client.get(url).status_code, 404)

    def test_unmoderated_messages_not_included(self):
        recipient = Person.objects.first()
        first = Message.objects.create(
            writeitinstance=self.writeitinstance,
            public=True,
            confirmated=True,
            moderated=True,
            subject='m: yes, p: yes, c: yes',
            slug='m:yes, p:yes, c:yes',
            content='example content',
            author_name='joe bloggs',
            author_email='joe@example.com',
            persons=[recipient],
        )
        Message.objects.create(
            writeitinstance=self.writeitinstance,
            public=True,
            confirmated=True,
            moderated=None,
            subject='m: null, p: yes, c: yes',
            slug='m:null, p:yes, c:yes',
            content='example content',
            author_name='joe bloggs',
            author_email='joe@example.com',
            persons=[recipient],
        )
        Message.objects.create(
            writeitinstance=self.writeitinstance,
            public=True,
            confirmated=True,
            moderated=False,
            subject='m: no, p: yes, c: yes',
            slug='m:no, p:yes, c:yes',
            content='example content',
            author_name='joe bloggs',
            author_email='joe@example.com',
            persons=[recipient],
        )
        url = reverse('all-messages-from-the-same-author-as', subdomain=self.message.writeitinstance.slug,
            kwargs={
                'message_slug': first.slug
            })
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('m: yes, p: yes, c: yes', response.content)
        self.assertIn('m: null, p: yes, c: yes', response.content)
        self.assertNotIn('m: no, p: yes, c: yes', response.content)

    def test_stricter_anonymisation_no_link_just_on_email(self):
        recipient = Person.objects.first()
        Message.objects.create(
            writeitinstance=self.writeitinstance,
            public=True,
            confirmated=True,
            moderated=True,
            subject='joe as name, joe as email',
            content='Random content',
            author_name='Joe',
            author_email='joe@example.com',
            persons=[recipient],
        )
        Message.objects.create(
            writeitinstance=self.writeitinstance,
            public=True,
            confirmated=True,
            moderated=True,
            subject='anon as name, joe as email',
            content='More random content',
            author_name='Anon',
            author_email='joe@example.com',
            persons=[recipient],
        )
        Message.objects.create(
            writeitinstance=self.writeitinstance,
            public=True,
            confirmated=True,
            moderated=True,
            subject='joe as name, joseph as email',
            content='A bit more content',
            author_name='Joe',
            author_email='joseph@example.com',
            persons=[recipient],
        )
        config = self.writeitinstance.config
        config.email_and_name_must_match = True
        config.save()

        def get_url(message_slug):
            return reverse(
                'all-messages-from-the-same-author-as',
                subdomain=self.writeitinstance.slug,
                kwargs={
                    'message_slug': message_slug
                })

        url = get_url('joe-as-name-joseph-as-email')
        response = self.client.get(url)
        messages_for_page = response.context['object_list']
        self.assertEquals(1, len(messages_for_page))
        self.assertEquals(
            messages_for_page[0].subject,
            'joe as name, joseph as email')

        url = get_url('anon-as-name-joe-as-email')
        response = self.client.get(url)
        messages_for_page = response.context['object_list']
        self.assertEquals(1, len(messages_for_page))
        self.assertEquals(
            messages_for_page[0].subject,
            'anon as name, joe as email')

        url = get_url('joe-as-name-joe-as-email')
        response = self.client.get(url)
        messages_for_page = response.context['object_list']
        self.assertEquals(1, len(messages_for_page))
        self.assertEquals(
            messages_for_page[0].subject,
            'joe as name, joe as email')
