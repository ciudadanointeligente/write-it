# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from nuntium.models import WriteItInstance
from subdomains.utils import reverse
from popit.models import Person
from nuntium.forms import WhoForm

# This method adds a session to a request
# But I could not do anything with it
# def add_session_to_request(request):
#     """Annotate a request object with a session"""
#     middleware = SessionMiddleware()
#     middleware.process_request(request)
#     request.session.save()


class MessageCreationTestCase(TestCase):
    def setUp(self):
        super(MessageCreationTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.get(id=1)
        self.person1 = Person.objects.get(id=1)
        self.person2 = Person.objects.get(id=2)
        self.writeitinstance.add_person(self.person1)
        self.writeitinstance.add_person(self.person2)

    def test_step_who_doesn_have_persons_without_contacts_self_client(self):
        '''The who step of creating a message doesn't have a person without contacts'''
        self.assertTrue(self.person1.contact_set.all())
        self.person2.contact_set.all().delete()

        url = reverse('write_message_step',
            subdomain=self.writeitinstance.slug,
            kwargs={'step': 'who'})

        response = self.client.get(url)
        who_form = response.context['form']
        self.assertIsInstance(who_form, WhoForm)
        self.assertIn(self.person1, who_form.fields['persons'].queryset)
        self.assertNotIn(self.person2, who_form.fields['persons'].queryset)

    # def test_step_who_with_requestfactory(self):
    #     request = self.factory.get(url)
    #     add_session_to_request(request)
    #     request.user = AnonymousUser()
    #     respose_redirect = WriteMessageView.as_view(url_name="write_message_step")(request, step='who')
    #     request = self.factory.get(respose_redirect.url)
    #     request.subdomain = self.writeitinstance.slug
