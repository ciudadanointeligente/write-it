from django.test import TestCase
from nuntium.models import Message
#from popit.models import ApiInstance, Person

class TestMessages(TestCase):
    # def setUp(self):
    #     self.instance = ApiInstance(url="http://foo.com/api")
    #     self.person = Person(api_instance=self.instance, name="Bob")
    # we should wait for popit-django


    def test_create_message(self):
        message = Message.objects.create(content = 'message text 1')
        self.assertTrue(message)

