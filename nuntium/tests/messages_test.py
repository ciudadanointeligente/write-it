from django.test import TestCase
from nuntium.models import Message

class TestMessages(TestCase):

	def test_create_message(self):
		message = Message.objects.create(content = 'message text 1')
		self.assertTrue(message)

