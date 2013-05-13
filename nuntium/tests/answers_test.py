from global_test_case import GlobalTestCase as TestCase
from nuntium.models import Message, Answer
from popit.models import Person
from django.utils.translation import ugettext as _

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


	def test_answer_has_unicode(self):
		answer = Answer.objects.create(message=self.message, person=self.person, content="the answer to that is ...")

		expected_unicode = _("%(person)s said \"%(content)s\" to the message %(message)s") % {
			'person': self.person.name,
			'content': "the answer to that is ...",
			'message': self.message.subject
			}
		self.assertEquals(answer.__unicode__(), expected_unicode)
