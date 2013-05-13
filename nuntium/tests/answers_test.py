from global_test_case import GlobalTestCase as TestCase
from nuntium.models import Message, Answer
from popit.models import Person

class AnswerTestCase(TestCase):
	def setUp(self):
		super(AnswerTestCase, self).setUp()
		self.message = Message.objects.all()[0]
		self.person = Person.objects.all()[0]

	def test_create_an_answer(self):
		answer = Answer.objects.create(message=self.message, person=self.person, content="the answer to that is ...")

		self.assertTrue(answer)
		self.assertEquals(answer.message, self.message)
		self.assertEquals(answer.person, self.person)
		self.assertEquals(answer.content, "the answer to that is ...")
		self.assertTrue(answer.created is not None)