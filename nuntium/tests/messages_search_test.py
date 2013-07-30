# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from nuntium.search_indexes import MessageIndex
from nuntium.models import Message
from haystack import indexes
from haystack.fields import CharField

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

		rendered_text = index.text.prepare_template(self.first_message)

		self.assertTrue(self.first_message.subject in rendered_text)
		self.assertTrue(self.first_message.content in rendered_text)
		