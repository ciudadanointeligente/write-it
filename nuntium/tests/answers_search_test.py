# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from nuntium.search_indexes import AnswerIndex
from nuntium.models import Answer, Message
from haystack import indexes
from haystack.fields import CharField

class AnswerIndexTestCase(TestCase):
    def setUp(self):
        super(AnswerIndexTestCase, self).setUp()
        self.index = AnswerIndex()
        for message in Message.objects.all():
            message.confirmated = True
            message.save()

    def test_index_parts(self):
        

        self.assertIsInstance(self.index, indexes.SearchIndex)
        self.assertIsInstance(self.index, indexes.Indexable)

        self.assertEquals(self.index.get_model(), Answer)

        public_answers = Answer.objects.filter(message__in=Message.objects.public())
        first_answer = public_answers[0]
        public_answers_list = list(public_answers)

        self.assertQuerysetEqual(self.index.index_queryset(), [repr(r) for r in public_answers_list])

        self.assertTrue(self.index.text.document)
        self.assertTrue(self.index.text.use_template)

        indexed_text = self.index.text.prepare_template(first_answer)

        self.assertTrue(first_answer.content in indexed_text)
        self.assertTrue(first_answer.person.name in indexed_text)

        rendered_text = self.index.rendered.prepare_template(first_answer)
        self.assertTrue(first_answer.content in rendered_text)
        self.assertTrue(first_answer.person.name in rendered_text)






