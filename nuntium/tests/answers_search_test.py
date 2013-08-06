# coding=utf-8
from global_test_case import GlobalTestCase as TestCase, SearchIndexTestCase
from nuntium.search_indexes import AnswerIndex
from django.core.management import call_command
from subdomains.utils import reverse
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

class SearchAnswerAccess(SearchIndexTestCase):
    def setUp(self):
        super(SearchAnswerAccess, self).setUp()


    def test_access_the_url(self):
        #I don't like this test that much 
        #because it seems to be likely to break if I add more 
        #public messages
        #if it ever fails
        #well then I'll fix it
        url = reverse('search_messages')
        data = {
        'q':'Public Answer'
        }
        response = self.client.get(url, data=data)
        self.assertEquals(response.status_code, 200)

        #the first one the one that says "Public Answer" in example_data.yml
        expected_answer = Answer.objects.get(id=1)
        self.assertIn('page', response.context)
        results = response.context['page'].object_list

        self.assertGreaterEqual(len(results), 1)
        self.assertEquals(results[0].object.id, expected_answer.id)
