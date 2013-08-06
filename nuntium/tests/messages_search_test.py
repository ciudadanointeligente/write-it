# coding=utf-8
from global_test_case import GlobalTestCase as TestCase, SearchIndexTestCase
from nuntium.search_indexes import MessageIndex
from django.core.management import call_command
from nuntium.models import Message
from nuntium.forms import  MessageSearchForm, PerInstanceSearchForm
from haystack import indexes
from haystack.fields import CharField
from haystack.forms import SearchForm
from subdomains.utils import reverse
from nuntium.views import MessageSearchView
from nuntium.models import WriteItInstance, Confirmation, Answer
from django.views.generic.edit import FormView
from django.utils.unittest import skip
from haystack.views import SearchView
from django.utils.unittest import skip
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

        indexed_text = self.index.text.prepare_template(self.first_message)

        self.assertTrue(self.first_message.subject in indexed_text)
        self.assertTrue(self.first_message.content in indexed_text)


        self.assertEquals(self.index.writeitinstance.model_attr, 'writeitinstance__id')


        self.assertEquals(self.index.writeitinstance.prepare(self.first_message), self.first_message.writeitinstance.id)
        #rendered
        # self.assertFalse(self.index.rendered.indexed)
        # self.assertIsInstance(self.index.rendered, CharField)
        # self.assertTrue(self.index.rendered.use_template)
        # self.assertEquals(self.index.rendered.template_name, 'nuntium/message/message_in_search_list.html')
        # rendered_text = self.index.rendered.prepare_template(self.first_message)

        # self.assertTrue(self.first_message.subject in rendered_text)
        # self.assertTrue(self.first_message.content in rendered_text)


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
            confirmated=True,
            writeitinstance= self.writeitinstance1,
            persons = [self.person1])

        self.assertIn(confirmated_message, self.index.index_queryset())
        self.assertNotIn(non_message, self.index.index_queryset())


    def test_it_does_not_search_within_non_moderated_messages(self):
        self.writeitinstance1.moderation_needed_in_all_messages = True
        self.writeitinstance1.save()
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Fiera es una perra feroz2', 
            writeitinstance= self.writeitinstance1,
            persons = [self.person1])
        message.recently_confirmated()

        #message is confirmed (or whatever way you spell it)
        #but it was written in an instance in wich all messages need moderation,
        #and therefore it needs to be moderated before it is shown in the searches

        self.assertNotIn(message, self.index.index_queryset())




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




class SearchMessageAccess(SearchIndexTestCase):
    def setUp(self):
        super(SearchMessageAccess, self).setUp()


    def test_access_the_url(self):
        #I don't like this test that much 
        #because it seems to be likely to break if I add more 
        #public messages
        #if it ever fails
        #well then I'll fix it
        url = reverse('search_messages')
        data = {
        'q':'Content'
        }
        response = self.client.get(url, data=data)
        self.assertEquals(response.status_code, 200)

        #the first one the one that says "Public Answer" in example_data.yml
        expected_answer = Message.objects.get(id=2)
        self.assertIn('page', response.context)
        results = response.context['page'].object_list

        self.assertGreaterEqual(len(results), 1)
        self.assertEquals(results[0].object.id, expected_answer.id)


class PerInstanceSearchFormTestCase(SearchIndexTestCase):
    def setUp(self):
        super(PerInstanceSearchFormTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.all()[0]


    #@skip("need to index writeitinstance for messages")
    def test_per_instance_search_form(self):
        form = PerInstanceSearchForm(writeitinstance=self.writeitinstance)
        self.assertIsInstance(form, SearchForm)

        ids_of_messages_returned_by_searchqueryset = []

        for result in form.searchqueryset:
            if result.content_type() == "nuntium.message":
                ids_of_messages_returned_by_searchqueryset.append(result.object.id)


        public_messages = Message.objects.public().filter(writeitinstance=self.writeitinstance)

        ids_of_public_messages_in_writeitinstance = [r.id for r in public_messages]

        self.assertItemsEqual(ids_of_public_messages_in_writeitinstance, ids_of_messages_returned_by_searchqueryset)



