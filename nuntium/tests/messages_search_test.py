# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from nuntium.search_indexes import MessageIndex
from nuntium.models import Message
from nuntium.forms import  MessageSearchForm
from haystack import indexes
from haystack.fields import CharField
from haystack.forms import SearchForm
from subdomains.utils import reverse
from nuntium.views import MessageSearchView
from nuntium.models import WriteItInstance
from django.views.generic.edit import FormView
from django.utils.unittest import skip
from haystack.views import SearchView
from popit.models import Person

class MessagesSearchTestCase(TestCase):
    def setUp(self):
        super(MessagesSearchTestCase, self).setUp()
        self.first_message = Message.objects.all()[0]
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.person1 = Person.objects.all()[0]
        self.person2 = Person.objects.all()[1]
        self.index = MessageIndex()
        for message in Message.objects.all():
            message.confirmated = True
            message.save()


    def test_messages_index(self):

        public_messages = list(Message.objects.filter(public=True))

        self.assertIsInstance(self.index, indexes.SearchIndex)
        self.assertIsInstance(self.index, indexes.Indexable)

        self.assertEquals(self.index.get_model(), Message)

        self.assertQuerysetEqual(self.index.index_queryset(), [repr(r) for r in public_messages])

        self.assertIsInstance(self.index.text, CharField)
        self.assertTrue(self.index.text.use_template)

        rendered_text = self.index.text.prepare_template(self.first_message)

        self.assertTrue(self.first_message.subject in rendered_text)
        self.assertTrue(self.first_message.content in rendered_text)


    def test_it_does_not_search_within_private_messages(self):
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Fiera es una perra feroz', 
            public=False,
            writeitinstance= self.writeitinstance1,
            persons = [self.person1])

        self.assertNotIn(message, self.index.index_queryset())

    def test_it_does_not_search_within_non_confirmated_messages(self):
        non_message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Fiera es una perra feroz', 
            writeitinstance= self.writeitinstance1,
            persons = [self.person1])

        confirmated_message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Fiera es una perra feroz2', 
            writeitinstance= self.writeitinstance1,
            confirmated = True,
            persons = [self.person1])

        self.assertIn(confirmated_message, self.index.index_queryset())
        self.assertNotIn(non_message, self.index.index_queryset())






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
        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertIsInstance(response.context['form'], MessageSearchForm)


    def test_search_view(self):
        view = MessageSearchView()

        self.assertIsInstance(view, SearchView)
        self.assertEquals(view.form_class, MessageSearchForm)
        self.assertEquals(view.template, 'nuntium/search.html')

