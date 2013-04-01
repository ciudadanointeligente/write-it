from django.test import TestCase
from nuntium.models import Message

class TestPerson(TestCase):

	def test_create_person(self):
		person = Person.objects.create(name = 'Name', last_name = 'Last-Name')
		self.assertTrue(person)

