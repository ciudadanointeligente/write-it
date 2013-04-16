from django.test import TestCase

class MessageFormTestCase(TestCase):

    def setUp(self):
        self.api_instance1 = ApiInstance.objects.create(url='http://popit.org/api/v1')
        self.person1 = Person.objects.create(api_instance=self.api_instance1, name= 'Person 1')
        self.contact_type1 = ContactType.objects.create(name= 'e-mail',label_name='Electronic Mail')
        self.contact1 = Contact.objects.create(person=self.person1, contact_type=self.contact_type1, value= 'test@test.com')
        self.instance1 = Instance.objects.create(name='instance 1', slug= 'instance-1', api_instance= api_instance1)

