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
from django.views.generic.edit import FormView
from django.utils.unittest import skip
from haystack.views import SearchView

class MessagesSearchTestCase(TestCase):
	def setUp(self):
		super(MessagesSearchTestCase, self).setUp()
		self.first_message = Message.objects.all()[0]


	def test_messages_index(self):
		index = MessageIndex()
		public_messages = list(Message.objects.filter(public=True))

		self.assertIsInstance(index, indexes.SearchIndex)
		self.assertIsInstance(index, indexes.Indexable)

		self.assertEquals(index.get_model(), Message)

		self.assertQuerysetEqual(index.index_queryset(), [repr(r) for r in public_messages])

		self.assertIsInstance(index.text, CharField)
		self.assertTrue(index.text.use_template)

		rendered_text = index.text.prepare_template(self.first_message)

		self.assertTrue(self.first_message.subject in rendered_text)
		self.assertTrue(self.first_message.content in rendered_text)


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

		