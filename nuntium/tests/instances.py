# coding=utf-8
from django.test import TestCase
from django.core.urlresolvers import reverse
from nuntium.models import Instance, Message
from nuntium.views import MessageCreateForm
from contactos.models import Contact, ContactType
from popit.models import ApiInstance, Person
from django.utils.unittest import skip

class InstanceTestCase(TestCase):

    def setUp(self):
        self.api_instance1 = ApiInstance.objects.create(url='http://popit.org/api/v1')
        self.api_instance2 = ApiInstance.objects.create(url='http://popit.org/api/v2')
        self.person1 = Person.objects.create(api_instance=self.api_instance1, name= 'Person 1')
        self.contact_type1 = ContactType.objects.create(name= 'e-mail',label_name='Electronic Mail')
        self.contact1 = Contact.objects.create(person=self.person1, contact_type=self.contact_type1, value= 'test@test.com')


    def test_create_instance(self):
        instance = Instance.objects.create(name='instance 1', api_instance= self.api_instance1, slug='instance-1')
        self.assertTrue(instance)

    def test_instance_containning_several_messages(self):
        instance1 = Instance.objects.create(name='instance 1', api_instance= self.api_instance1)
        instance2 = Instance.objects.create(name='instance 2', api_instance= self.api_instance2)
        message1 = Message.objects.create(content='Content 1', subject='Subject 1', instance = instance1, persons=[self.person1])
        message2 = Message.objects.create(content='Content 2', subject='Subject 2', instance = instance1, persons=[self.person1])
        message3 = Message.objects.create(content='Content 3', subject='Subject 3', instance = instance2, persons=[self.person1])
        self.assertEquals(instance1.message_set.count(),2)
        self.assertEquals(message1.instance, instance1)
        self.assertEquals(message2.instance, instance1)
        self.assertEquals(instance2.message_set.count(),1)
        self.assertEquals(message3.instance, instance2)

class InstanceDetailView(TestCase):
    def setUp(self):
        self.api_instance1 = ApiInstance.objects.create(url='http://popit.org/api/v1')
        self.instance1 = Instance.objects.create(name='instance 1', api_instance= self.api_instance1, slug='instance-1')
        self.person1 = Person.objects.create(api_instance=self.api_instance1, name= 'Person 1')
        self.contact_type1 = ContactType.objects.create(name= 'e-mail',label_name='Electronic Mail')
        self.contact1 = Contact.objects.create(person=self.person1, contact_type=self.contact_type1, value= 'test@test.com')
    
    def test_detail_instance_view(self):
        url = reverse('instance_detail', kwargs={
            'slug':self.instance1.slug
            })
        self.assertTrue(url)
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'nuntium/instance_detail.html')
        self.assertEquals(response.context['instance'], self.instance1)
        self.assertTrue(response.context['form'])
        self.assertTrue(isinstance(response.context['form'],MessageCreateForm))
        self.assertEquals(response.status_code, 200)
    


    # @skip(u'falta un test')
    def test_message_creation_on_post_form(self):

        #spanish
        data = {
        'subject':u'Fiera no está',
        'content':u'¿Dónde está Fiera Feroz? en la playa?',
        'persons': [self.person1.id]
        }
        url = reverse('instance_detail', kwargs={
            'slug':self.instance1.slug
            })
        response = self.client.post(url, data, follow=True)
        self.assertEquals(response.status_code, 200)
        new_messages = Message.objects.all()
        self.assertTrue(new_messages.count()>0)






