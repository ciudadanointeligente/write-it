# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from django.core.urlresolvers import reverse
from nuntium.models import WriteItInstance, Message, Membership, Confirmation
from nuntium.views import MessageCreateForm
from contactos.models import Contact, ContactType
from popit.models import ApiInstance, Person
from django.utils.unittest import skip
from datetime import datetime
from django.contrib.auth.models import User

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
        expected_url = reverse('instance_detail', kwargs={
            'slug':writeitinstance1.slug
            })

        self.assertEquals(expected_url, writeitinstance1.get_absolute_url())


    def test_membership(self):
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)

        Membership.objects.create(writeitinstance=writeitinstance, person=self.person1)
        self.assertEquals(writeitinstance.persons.get(id=self.person1.id), self.person1)
        self.assertEquals(self.person1.writeit_instances.get(id=writeitinstance.id), writeitinstance)

class InstanceDetailView(TestCase):
    def setUp(self):
        super(InstanceDetailView,self).setUp()
        self.api_instance1 = ApiInstance.objects.all()[0]
        self.api_instance2 = ApiInstance.objects.all()[1]
        self.person1 = Person.objects.all()[0]
        self.writeitinstance1 = WriteItInstance.objects.all()[0]

    
    def test_detail_instance_view(self):
        url = reverse('instance_detail', kwargs={
            'slug':self.writeitinstance1.slug
            })
        self.assertTrue(url)
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'nuntium/instance_detail.html')
        self.assertEquals(response.context['writeitinstance'], self.writeitinstance1)
        self.assertTrue(response.context['form'])
        self.assertTrue(isinstance(response.context['form'],MessageCreateForm))
        self.assertEquals(response.status_code, 200)

    def test_list_only_public_messages(self):
        private_message = Message.objects.create(content='Content 1', subject='a private message', writeitinstance = self.writeitinstance1, persons=[self.person1], public=False)
        url = reverse('instance_detail', kwargs={
            'slug':self.writeitinstance1.slug
            })
        response = self.client.get(url)
        self.assertTrue('public_messages' in response.context)
        self.assertTrue(private_message not in response.context['public_messages'])




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
            public=False)

        confirmation_for_message2 = Confirmation.objects.create(message=message2)
        self.client.get(reverse('confirm', kwargs={'slug':confirmation_for_message2.key}))
        confirmation_for_private_message = Confirmation.objects.create(message=private_message)
        self.client.get(reverse('confirm', kwargs={'slug':confirmation_for_private_message.key}))

        

        url = reverse('instance_detail', kwargs={
            'slug':self.writeitinstance1.slug
            })

        response = self.client.get(url)
        

        #message1 is not confirmed so it should not be in the list
        #private_message is not in the list either
        #only message 2 is in the list because is public and confirmed

        self.assertTrue(message2 in response.context['public_messages'])
        self.assertTrue(message1 not in response.context['public_messages'])
        self.assertTrue(message3 in response.context['public_messages'])
        self.assertTrue(private_message not in response.context['public_messages'])



    def test_message_creation_on_post_form(self):

        #spanish
        data = {
        'subject':u'Fiera no está',
        'content':u'¿Dónde está Fiera Feroz? en la playa?',
        'persons': [self.person1.id]
        }
        url = reverse('instance_detail', kwargs={
            'slug':self.writeitinstance1.slug
            })
        response = self.client.post(url, data, follow=True)
        self.assertEquals(response.status_code, 200)
        new_messages = Message.objects.all()
        self.assertTrue(new_messages.count()>0)


    def test_after_the_creation_of_a_message_it_redirects(self):
        data = {
        'subject':u'Fiera no está',
        'content':u'¿Dónde está Fiera Feroz? en la playa?',
        'author_name':u"Felipe",
        'author_email':u"falvarez@votainteligente.cl",
        'persons': [self.person1.id]
        }
        url = reverse('instance_detail', kwargs={
            'slug':self.writeitinstance1.slug
            })
        response = self.client.post(url, data)

        self.assertTrue(response['Location'].endswith(url))






