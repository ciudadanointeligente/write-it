from global_test_case import GlobalTestCase as TestCase, popit_load_data
from subdomains.utils import reverse, get_domain
from django.core.urlresolvers import reverse as original_reverse
from ...models import WriteItInstance, Membership
from django.contrib.auth.models import User
from django.test.client import Client, RequestFactory
from ..views import WriteItInstanceUpdateView
from django.forms import ModelForm
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.translation import activate
from ..forms import WriteItInstanceBasicForm, WriteItInstanceAdvancedUpdateForm, \
                            WriteItInstanceCreateForm
from popit.models import Person, ApiInstance
from django.forms.models import model_to_dict
from contactos.models import Contact
from contactos.forms import ContactCreateForm
from ..forms import NewAnswerNotificationTemplateForm, ConfirmationTemplateForm
from mailit.forms import MailitTemplateForm
from django.utils.unittest import skipUnless, skip
from user_section_views_tests import UserSectionTestCase

class UpdateMyPopitInstancesTestCase(UserSectionTestCase):

    def setUp(self):
        super(UpdateMyPopitInstancesTestCase, self).setUp()
        self.user = User.objects.create_user(username="fieraferoz", password="feroz")


    def test_a_url_is_reachable(self):
        '''My popit instances url is reachable'''
        url = reverse('my-popit-instances')
        self.assertTrue(url)

    def test_it_brings_all_the_popit_apis(self):
        '''My popit apis admin page brings all my popit apis'''
        writeitinstance = WriteItInstance.objects.create(
            name='instance 1', 
            slug='instance-1',
            owner=self.user)


        instance1 = ApiInstance.objects.create(url="http://foo.com/api")
        instance2 = ApiInstance.objects.create(url="http://foo2.com/api")
        instance3 = ApiInstance.objects.create(url="http://foo3.com/api")

        fiera = Person.objects.create(api_instance=instance1, name="fiera")
        benito = Person.objects.create(api_instance=instance2, name="benito")
        non_related_person = Person.objects.create(api_instance=instance3, name="ac")

        Membership.objects.create(writeitinstance=writeitinstance, person=fiera)
        Membership.objects.create(writeitinstance=writeitinstance, person=benito)

        c = Client()

        c.login(username="fieraferoz", password="feroz")
        url = reverse('my-popit-instances')
        response = c.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('object_list', response.context)
        self.assertIn(instance1,response.context['object_list'])
        self.assertIn(instance2,response.context['object_list'])
        self.assertNotIn(instance3,response.context['object_list'])

        self.assertTemplateUsed(response, 'nuntium/profiles/your-popit-apis.html')
        self.assertTemplateUsed(response, 'base_edit.html')


    def test_I_can_only_access_if_I_logged_in(self):
        ''' I can only access my popit apis if Im logged in'''
        c = Client()

        # the following line is commented on porpouse
        # c.login(username="fieraferoz", password="feroz")
        # to show that c is not logged in
        url = reverse('my-popit-instances')

        response = c.get(url)
        self.assertRedirectToLogin(response, next_url=url)


    def test_there_is_a_url_where_you_can_update_a_popit_instance(self):
        '''There is a url to update a popit instance'''
        api_instance = ApiInstance.objects.first()
        url = reverse('update-popit-instance', kwargs={'pk':api_instance.pk})
        self.assertTrue(url)


    @skip("I'm gonna relate a popit instance and a WriteItInstance in some way first")
    def test_I_can_update_a_popit_instance(self):
        '''By posting I can update a popit instance'''
        api_instance = ApiInstance.objects.create(url=settings.TEST_POPIT_API_URL)

        url = reverse('update-popit-instance', kwargs={'pk':api_instance.pk})
        c = Client()
        c.login(username="fieraferoz", password="feroz")
        response = c.get(url)
        #I'm going to delete all the persons so I catch them again
        api_instance = ApiInstance.objects.get(url=settings.TEST_POPIT_API_URL)
        self.assertTrue(api_instance.person_set.all())
        
