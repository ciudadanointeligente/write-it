# coding=utf-8
from global_test_case import GlobalTestCase as TestCase, SearchIndexTestCase
from ..search_indexes import MessageIndex
from django.contrib.contenttypes.models import ContentType

from ..models import Message
from ..forms import MessageSearchForm, PerInstanceSearchForm
from haystack import indexes
from haystack.fields import CharField
from haystack.forms import SearchForm
from subdomains.utils import reverse
from instance.models import WriteItInstance
from ..views import MessageSearchView, PerInstanceSearchView
from haystack.views import SearchView
from popolo.models import Person
import urllib
import urlparse


class MessagesSearchTestCase(TestCase):
    def setUp(self):
        super(MessagesSearchTestCase, self).setUp()
        self.first_message = Message.objects.get(id=1)
        self.writeitinstance1 = WriteItInstance.objects.get(id=1)
        self.person1 = Person.objects.get(id=1)
        self.person2 = Person.objects.get(id=2)
        self.index = MessageIndex()
        for message in Message.objects.all():
            message.confirmated = True
            message.save()

    def test_messages_index(self):
        public_messages = list(Message.objects.filter(public=True))

        self.assertIsInstance(self.index, indexes.SearchIndex)
        self.assertIsInstance(self.index, indexes.Indexable)

        self.assertEquals(self.index.get_model(), Message)

        self.assertQuerysetEqual(self.index.index_queryset(), [repr(r) for r in public_messages], ordered=False)

        self.assertIsInstance(self.index.text, CharField)

        self.assertTrue(self.index.text.use_template)

        indexed_text = self.index.text.prepare_template(self.first_message)

        self.assertTrue(self.first_message.subject in indexed_text)
        self.assertTrue(self.first_message.content in indexed_text)

        self.assertEquals(self.index.writeitinstance.model_attr, 'writeitinstance__id')

        self.assertEquals(self.index.writeitinstance.prepare(self.first_message), self.first_message.writeitinstance.id)

    def test_it_does_not_search_within_private_messages(self):
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Fiera es una perra feroz',
            public=False,
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        self.assertNotIn(message, self.index.index_queryset())

    def test_it_does_not_search_within_non_confirmated_messages(self):
        non_message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Fiera es una perra feroz',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        confirmated_message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Fiera es una perra feroz2',
            confirmated=True,
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        self.assertIn(confirmated_message, self.index.index_queryset())
        self.assertNotIn(non_message, self.index.index_queryset())

    def test_it_does_not_search_within_non_moderated_messages(self):
        self.writeitinstance1.config.moderation_needed_in_all_messages = True
        self.writeitinstance1.save()
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Fiera es una perra feroz2',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        message.recently_confirmated()

        # message is confirmed (or whatever way you spell it)
        # but it was written in an instance in wich all messages need moderation,
        # and therefore it needs to be moderated before it is shown in the searches

        self.assertNotIn(message, self.index.index_queryset())


class MessageSearchFormTestCase(TestCase):
    def setUp(self):
        super(MessageSearchFormTestCase, self).setUp()

    def test_it_is_a_search_form(self):
        form = MessageSearchForm()

        self.assertIsInstance(form, SearchForm)


class MessageSearchViewTestCase(TestCase):
    def setUp(self):
        super(MessageSearchViewTestCase, self).setUp()

    def test_access_the_search_url(self):
        url = reverse('search_messages')
        url += '/'
        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertIsInstance(response.context['form'], MessageSearchForm)

    def test_search_view(self):
        view = MessageSearchView()

        self.assertIsInstance(view, SearchView)
        self.assertEquals(view.form_class, MessageSearchForm)
        self.assertEquals(view.template, 'nuntium/search.html')


class SearchMessageAccess(SearchIndexTestCase):
    def setUp(self):
        super(SearchMessageAccess, self).setUp()

    def test_access_the_url(self):
        # I don't like this test that much
        # because it seems to be likely to break if I add more
        # public messages
        # if it ever fails
        # well then I'll fix it
        url = reverse('search_messages')
        url += "/"
        data = {'q': 'Content'}

        url_parts = list(urlparse.urlparse(url))
        url_parts[4] = urllib.urlencode(data)
        url_with_parameters = urlparse.urlunparse(url_parts)

        response = self.client.get(url_with_parameters)
        self.assertEquals(response.status_code, 200)

        # the first one the one that says "Public Answer" in example_data.yml
        expected_answer = Message.objects.get(id=2)
        self.assertIn('page', response.context)
        results = response.context['page'].object_list

        self.assertGreaterEqual(len(results), 1)
        self.assertEquals(results[0].object.id, expected_answer.id)


class PerInstanceSearchFormTestCase(SearchIndexTestCase):
    def setUp(self):
        super(PerInstanceSearchFormTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.get(id=1)

    def test_per_instance_search_form(self):
        form = PerInstanceSearchForm(writeitinstance=self.writeitinstance)
        self.assertIsInstance(form, SearchForm)

        ids_of_messages_returned_by_searchqueryset = []
        content_type = ContentType.objects.get(model='message')

        for result in form.searchqueryset:
            if result.content_type() == content_type.app_label + ".message":
                ids_of_messages_returned_by_searchqueryset.append(result.object.id)

        public_messages = Message.public_objects.filter(writeitinstance=self.writeitinstance)

        ids_of_public_messages_in_writeitinstance = [r.id for r in public_messages]

        self.assertItemsEqual(ids_of_public_messages_in_writeitinstance, ids_of_messages_returned_by_searchqueryset)

    def test_per_instance_search_view(self):
        view = PerInstanceSearchView()
        self.assertIsInstance(view, SearchView)
        self.assertEquals(view.form_class, PerInstanceSearchForm)
        self.assertEquals(view.template, 'nuntium/instance_search.html')

    def test_per_instance_search_url(self):
        url = reverse('instance_search', subdomain=self.writeitinstance.slug)

        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)

        self.assertTemplateUsed(response, 'nuntium/instance_search.html')

        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PerInstanceSearchForm)
