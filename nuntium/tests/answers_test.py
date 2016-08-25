from global_test_case import GlobalTestCase as TestCase
from ..models import Message, Answer
from instance.models import PopoloPerson
from django.utils.translation import ugettext as _


class AnswerTestCase(TestCase):
    def setUp(self):
        super(AnswerTestCase, self).setUp()
        self.message = Message.objects.get(id=1)
        self.person = PopoloPerson.objects.get(id=1)
        #There is no membership for this guy to any writeitInstance
        self.person_not_in_the_instance = PopoloPerson.objects.get(id=2)

    def test_create_an_answer(self):
        answer = Answer.objects.create(message=self.message,
            person=self.person,
            content=u"the answer to that is ...",
            content_html=u"<p>the answer to that is ...</p>")

        self.assertTrue(answer.id)
        self.assertEquals(answer.message, self.message)
        self.assertEquals(answer.person, self.person)
        self.assertEquals(answer.content, u"the answer to that is ...")
        self.assertEquals(answer.content_html, u"<p>the answer to that is ...</p>")
        self.assertTrue(answer.created is not None)

    def test_answer_has_unicode(self):
        answer = Answer.objects.create(message=self.message, person=self.person, content="the answer to that is ...")

        expected_unicode = _("%(person)s said \"%(content)s\" to the message %(message)s") % {
            'person': self.person.name,
            'content': "the answer to that is ...",
            'message': self.message.subject
            }
        self.assertEquals(answer.__unicode__(), expected_unicode)

    def test_create_answer_with_only_a_message(self):
        answer = Answer(message=self.message)

        self.assertTrue(answer)

    def test_assign_not_the_person_and_raise_error(self):
        answer = Answer(message=self.message)

        answer.person = self.person_not_in_the_instance
        with self.assertRaises(AttributeError):
            answer.save()

    def test_answers_can_only_be_answered_by_a_person_in_the_instance(self):
        with self.assertRaises(AttributeError):
            Answer.objects.create(
                message=self.message,
                person=self.person_not_in_the_instance,
                content="the answer to that is ...",
                )
