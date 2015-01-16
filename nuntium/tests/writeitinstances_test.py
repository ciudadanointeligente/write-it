# coding=utf-8
from global_test_case import GlobalTestCase as TestCase, popit_load_data
from django.core.urlresolvers  import reverse
from ..models import WriteItInstance, Message, Membership, Confirmation, Moderation
from ..views import MessageCreateForm, PerInstanceSearchForm
from contactos.models import Contact, ContactType
from popit.models import ApiInstance, Person
from django.utils.unittest import skipUnless
from datetime import datetime
from django.contrib.auth.models import User
from django.utils.translation import activate
from django.utils.translation import ugettext as _
from django.conf import settings

class InstanceTestCase(TestCase):

    def setUp(self):
        super(InstanceTestCase,self).setUp()
        self.api_instance1 = ApiInstance.objects.all()[0]
        self.api_instance2 = ApiInstance.objects.all()[1]
        self.person1 = Person.objects.all()[0]

        self.owner = User.objects.all()[0]

    def test_create_instance(self):
        writeitinstance = WriteItInstance.objects.create(
            name='instance 1', 
            slug='instance-1',
            owner=self.owner)
        self.assertTrue(writeitinstance.id)
        self.assertEquals(writeitinstance.name, 'instance 1')
        self.assertEquals(writeitinstance.slug, 'instance-1')
        self.assertEquals(writeitinstance.owner, self.owner)
        self.assertTrue(writeitinstance.allow_messages_using_form)
        self.assertFalse(writeitinstance.notify_owner_when_new_answer)
        self.assertTrue(writeitinstance.autoconfirm_api_messages)

    def test_owner_related_name(self):
        writeitinstance = WriteItInstance.objects.create(
            name='instance 1', 
            slug='instance-1',

            owner=self.owner)

        self.assertIn(writeitinstance, self.owner.writeitinstances.all())

    def test_moderation_needed_in_all_messages(self):
        
        writeitinstance = WriteItInstance.objects.create(
            name='instance 1', 
            slug='instance-1',
            moderation_needed_in_all_messages=False, 
            owner=self.owner)

        self.assertTrue(writeitinstance)


    def test_instance_unicode(self):
        writeitinstance = WriteItInstance.objects.all()[0]
        self.assertEquals(writeitinstance.__unicode__() , writeitinstance.name)

    def test_instance_containning_several_messages(self):
        writeitinstance1 = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)
        writeitinstance2 = WriteItInstance.objects.create(name='instance 2', slug='instance-2', owner=self.owner)
        message1 = Message.objects.create(content='Content 1', subject='Subject 1', writeitinstance = writeitinstance1, persons=[self.person1])
        message2 = Message.objects.create(content='Content 2', subject='Subject 2', writeitinstance = writeitinstance1, persons=[self.person1])
        message3 = Message.objects.create(content='Content 3', subject='Subject 3', writeitinstance = writeitinstance2, persons=[self.person1])
        self.assertEquals(writeitinstance1.message_set.count(),2)
        self.assertEquals(message1.writeitinstance, writeitinstance1)
        self.assertEquals(message2.writeitinstance, writeitinstance1)
        self.assertEquals(writeitinstance2.message_set.count(),1)
        self.assertEquals(message3.writeitinstance, writeitinstance2)

    def test_get_absolute_url(self):
        writeitinstance1 = WriteItInstance.objects.all()[0]
        expected_url = reverse('instance_detail',
            kwargs={'slug':writeitinstance1.slug})

        self.assertEquals(expected_url, writeitinstance1.get_absolute_url())


    def test_get_absolute_url_i18n(self):
        activate("es")
        writeitinstance1 = WriteItInstance.objects.all()[0]
        self.assertTrue(writeitinstance1.get_absolute_url().startswith('/es/'))
        response = self.client.get(writeitinstance1.get_absolute_url())
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'nuntium/instance_detail.html')


    def test_get_non_existing_instance(self):
        url = reverse('instance_detail',
            kwargs={'slug':"non-existing-slug"})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_membership(self):
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)

        Membership.objects.create(writeitinstance=writeitinstance, person=self.person1)
        self.assertEquals(writeitinstance.persons.get(id=self.person1.id), self.person1)
        self.assertEquals(self.person1.writeit_instances.get(id=writeitinstance.id), writeitinstance)

    @skipUnless(settings.LOCAL_POPIT, "No local popit running")
    def test_create_an_instance_and_load_persons_from_an_api(self):
        # We have a popit running locally using the 
        # start_local_popit_api.bash script
        popit_load_data()
        #loading data into the popit-api
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)

        writeitinstance.load_persons_from_a_popit_api(settings.TEST_POPIT_API_URL)

        self.assertEquals(writeitinstance.persons.all().count(), 2)

        raton = Person.objects.get(name='Ratón Inteligente')
        fiera = Person.objects.get(name="Fiera Feroz")

        self.assertIn(raton, [r for r in writeitinstance.persons.all()])
        self.assertIn(fiera, [r for r in writeitinstance.persons.all()])

from nuntium.popit_api_instance import PopitApiInstance
from requests.exceptions import ConnectionError

class WriteItInstanceLoadingPeopleFromAPopitApiTestCase(TestCase):
    def setUp(self):
        super(WriteItInstanceLoadingPeopleFromAPopitApiTestCase, self).setUp()
        self.api_instance1 = ApiInstance.objects.all()[0]
        self.api_instance2 = ApiInstance.objects.all()[1]
        self.person1 = Person.objects.all()[0]

        self.owner = User.objects.all()[0]

    def test_load_persons_from_a_popit_api(self):
        '''Loading persons from a popit api'''
        popit_load_data()
        popit_api_instance, created = PopitApiInstance.objects.get_or_create(url =settings.TEST_POPIT_API_URL)
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)
        writeitinstance.relate_with_persons_from_popit_api_instance(popit_api_instance)

        self.assertEquals(writeitinstance.persons.all().count(), 2)

        raton = Person.objects.get(name='Ratón Inteligente')
        fiera = Person.objects.get(name="Fiera Feroz")

        self.assertIn(raton, [r for r in writeitinstance.persons.all()])
        self.assertIn(fiera, [r for r in writeitinstance.persons.all()])

    def test_it_returns_a_tuple(self):
        '''Returns a tuple'''
        popit_load_data()
        popit_api_instance, created = PopitApiInstance.objects.get_or_create(url =settings.TEST_POPIT_API_URL)
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)
        result= writeitinstance.relate_with_persons_from_popit_api_instance(popit_api_instance)
        self.assertIsInstance(result, tuple)
        self.assertTrue(result[0])
        self.assertIsNone(result[1])

    def test_it_returns_false_when_theres_a_problem(self):
        '''When there's a problem it returns false and the problem in the tuple'''
        non_existing_url = "http://nonexisting.url"
        popit_api_instance = PopitApiInstance.objects.create(url=non_existing_url)
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)
        result= writeitinstance.relate_with_persons_from_popit_api_instance(popit_api_instance)
        self.assertIsInstance(result, tuple)
        self.assertFalse(result[0])
        self.assertIsInstance(result[1], ConnectionError)




from ..models import WriteitInstancePopitInstanceRecord
class PopitWriteitRelationRecord(TestCase):
    '''
    This set of tests are intended to solve the problem
    of relating a writeit instance and a popit instance
    in some for that does not force them to be 
    1-1
    '''

    def setUp(self):
        self.writeitinstance = WriteItInstance.objects.first()
        self.api_instance =  ApiInstance.objects.first()
        self.owner = User.objects.first()

    def test_instanciate(self):
        '''Instanciate a WriteitInstancePopitInstanceRelation'''
        record = WriteitInstancePopitInstanceRecord\
            .objects.create(
                writeitinstance = self.writeitinstance,
                popitapiinstance = self.api_instance
            )

        self.assertTrue(record)
        self.assertEquals(record.writeitinstance, self.writeitinstance)
        self.assertEquals(record.popitapiinstance, self.api_instance)
        self.assertTrue(record.updated)
        self.assertTrue(record.created)

    def test_unicode(self):
        '''A WriteitInstancePopitInstanceRelation has a __unicode__ method'''
        record = WriteitInstancePopitInstanceRecord\
            .objects.create(
                writeitinstance = self.writeitinstance,
                popitapiinstance = self.api_instance
            )
        expected_unicode = "The people from http://popit.org/api/v1 was loaded into instance 1"
        self.assertEquals(record.__unicode__(), expected_unicode)



    @skipUnless(settings.LOCAL_POPIT, "No local popit running")
    def test_it_is_created_automatically_when_fetching_a_popit_instance(self):
        '''create automatically a record when fetching a popit instance'''

        popit_load_data()
        #loading data into the popit-api
        writeitinstance = WriteItInstance.objects.create(\
            name='instance 1', \
            slug='instance-1', \
            owner=self.owner)

        writeitinstance.load_persons_from_a_popit_api(settings.TEST_POPIT_API_URL)

        popit_instance = ApiInstance.objects.get(url=settings.TEST_POPIT_API_URL)

        record = WriteitInstancePopitInstanceRecord.objects.get(\
            writeitinstance=writeitinstance,
            popitapiinstance=popit_instance
            )

        self.assertTrue(record)
        self.assertTrue(record.updated)
        self.assertTrue(record.created)

    def test_what_if_the_url_doesnt_exist(self):
        '''It solves the problem when there is no popit api running'''
        writeitinstance = WriteItInstance.objects.create(\
            name='instance 1', \
            slug='instance-1', \
            owner=self.owner)

        non_existing_url = "http://nonexisting.url"
        writeitinstance.load_persons_from_a_popit_api("http://nonexisting.url")
        popit_instance_count = ApiInstance.objects.filter(url="http://nonexisting.url").count()

        self.assertFalse(popit_instance_count)
        
    @skipUnless(settings.LOCAL_POPIT, "No local popit running")
    def test_it_should_be_able_to_update_twice(self):
        '''It should be able to update all data twice'''
        popit_load_data()
        #loading data into the popit-api
        writeitinstance = WriteItInstance.objects.create(\
            name='instance 1', \
            slug='instance-1', \
            owner=self.owner)

        writeitinstance.load_persons_from_a_popit_api(settings.TEST_POPIT_API_URL)

        popit_instance = ApiInstance.objects.get(url=settings.TEST_POPIT_API_URL)

        
        writeitinstance.load_persons_from_a_popit_api(settings.TEST_POPIT_API_URL)

        record = WriteitInstancePopitInstanceRecord.objects.get(\
            writeitinstance=writeitinstance,
            popitapiinstance=popit_instance
            )

        self.assertNotEqual(record.created, record.updated)



class InstanceDetailView(TestCase):
    def setUp(self):
        super(InstanceDetailView, self).setUp()
        self.api_instance1 = ApiInstance.objects.all()[0]
        self.api_instance2 = ApiInstance.objects.all()[1]
        self.person1 = Person.objects.all()[0]
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.url = self.writeitinstance1.get_absolute_url()

    
    def test_detail_instance_view(self):
        #I'm removing this because it has been already tested
        #self.assertTrue(url)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'nuntium/instance_detail.html')
        self.assertEquals(response.context['writeitinstance'], self.writeitinstance1)
        self.assertTrue(response.context['form'])
        self.assertTrue(isinstance(response.context['form'],MessageCreateForm))
        self.assertEquals(response.status_code, 200)

    def test_instance_view_has_a_search_form(self):
        response = self.client.get(self.url)

        self.assertIn('search_form', response.context)

        self.assertIsInstance(response.context['search_form'], PerInstanceSearchForm)

        self.assertEquals(response.context['search_form'].writeitinstance, self.writeitinstance1)


    def test_list_only_public_messages(self):
        private_message = Message.objects.create(content='Content 1', subject='a private message', writeitinstance = self.writeitinstance1, persons=[self.person1], public=False)
        response = self.client.get(self.url)

        self.assertTrue('public_messages' in response.context)
        self.assertTrue(private_message not in response.context['public_messages'])


    def test_in_moderation_needed_instances_does_not_show_a_confirmated_but_not_moderated(self):
        self.writeitinstance1.moderation_needed_in_all_messages = True

        self.writeitinstance1.save()
        message = Message.objects.create(
            content='Content 3', 
            subject='Subject 3', 
            writeitinstance = self.writeitinstance1, 
            confirmated = True,
            persons=[self.person1]
            )

        confirmation = Confirmation.objects.create(message=message)
        self.client.get(confirmation.get_absolute_url())

        #ok it is now confirmated but it is not moderated

        url = self.writeitinstance1.get_absolute_url()

        response = self.client.get(self.url)

        self.assertNotIn(message, response.context['public_messages'])








    def test_list_only_confirmed_and_public_messages(self):
        message1 = self.writeitinstance1.message_set.all()[0]
        message2 = self.writeitinstance1.message_set.all()[1]
        message3 = Message.objects.create(
            content='Content 3', 
            subject='Subject 3', 
            writeitinstance = self.writeitinstance1, 
            confirmated = True,
            persons=[self.person1]
            )
        private_message = Message.objects.create(content='Content 1', 
            subject='a private message', 
            writeitinstance = self.writeitinstance1, 
            persons=[self.person1], 
            confirmated = True,
            public=False)

        confirmation_for_message2 = Confirmation.objects.create(message=message2)
        self.client.get(confirmation_for_message2.get_absolute_url())


        #now i need to moderate this
        self.client.get(private_message.moderation.get_success_url())

        confirmation_for_private_message = Confirmation.objects.create(message=private_message)
        self.client.get(reverse('confirm', kwargs={'slug':confirmation_for_private_message.key}))

        

        url = self.writeitinstance1.get_absolute_url()
        
        response = self.client.get(self.url)
        
        
        #message1 is not confirmed so it should not be in the list
        #private_message is not in the list either
        #only message 2 is in the list because is public and confirmed

        self.assertIn(message2, response.context['public_messages'])
        self.assertNotIn(message1, response.context['public_messages'])
        self.assertIn(message3, response.context['public_messages'])
        self.assertNotIn(private_message, response.context["public_messages"])



    def test_message_creation_on_post_form(self):

        #spanish
        data = {
        'author_email':u'falvarez@votainteligente.cl',
        'author_name':u'feli',
        'subject':u'Fiera no está',
        'content':u'¿Dónde está Fiera Feroz? en la playa?',
        'persons': [self.person1.id]
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEquals(response.status_code, 200)
        new_messages = Message.objects.filter(subject='Fiera no está')
        self.assertTrue(new_messages.count()>0)
        self.assertEquals(len(response.context["form"].errors), 0)

    def test_I_get_an_acknoledgement_for_creating_a_message(self):
        #spanish
        data = {
        'subject':u'Fiera no está',
        'author_email':u'falvarez@votainteligente.cl',
        'author_name':u'feli',
        'public':True,
        'content':u'¿Dónde está Fiera Feroz? en la playa?',
        'persons': [self.person1.id]
        }

        response = self.client.post(self.url, data, follow=True)
        self.assertEquals(response.status_code, 200)
        expected_acknoledgments = _("Thanks for submitting your message, please check your email and click on the confirmation link")

        self.assertContains(response, expected_acknoledgments)

        all_messages, all_retrieved = response.context["messages"]._get()

        self.assertEquals(len(all_messages), 1)
        self.assertEquals(all_messages[0].__str__(), expected_acknoledgments)

    def test_after_the_creation_of_a_message_it_redirects(self):
        data = {
        'subject':u'Fiera no está',
        'content':u'¿Dónde está Fiera Feroz? en la playa?',
        'author_name':u"Felipe",
        'author_email':u"falvarez@votainteligente.cl",
        'persons': [self.person1.id]
        }
        url = self.writeitinstance1.get_absolute_url()
        response = self.client.post(self.url, data)

        self.assertRedirects(response, url)


    def test_if_the_instance_needs_moderation_in_all_messages(self):
        self.writeitinstance1.moderation_needed_in_all_messages = True
        self.writeitinstance1.save()
        data = {
            'subject':u'Fiera no está',
            'content':u'¿Dónde está Fiera Feroz? en la playa?',
            'author_name':u"Felipe",
            'public': True,
            'author_email':u"falvarez@votainteligente.cl",
            'persons': [self.person1.id]
        }

        url = self.writeitinstance1.get_absolute_url()
        response = self.client.post(self.url, data, follow=True)

        expected_acknoledgments = _("Thanks for submitting your message, please check your email and click on the confirmation link, after that your message will be waiting form moderation")


        self.assertContains(response, expected_acknoledgments)









