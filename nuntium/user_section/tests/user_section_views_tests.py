from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings
from django.db.models import Q
from django.test.client import Client, RequestFactory
from django.utils.translation import activate
from django.utils.unittest import skipUnless
from popit.models import Person
from mailit.forms import MailitTemplateForm
from global_test_case import GlobalTestCase as TestCase, popit_load_data

from nuntium.models import WriteItInstance, WriteItInstanceConfig, WriteitInstancePopitInstanceRecord
from nuntium.user_section.views import WriteItInstanceUpdateView, WriteItInstanceApiDocsView
from nuntium.user_section.forms import WriteItInstanceBasicForm, \
    WriteItInstanceAdvancedUpdateForm, WriteItInstanceCreateForm, \
    NewAnswerNotificationTemplateForm, ConfirmationTemplateForm


class UserSectionTestCase(TestCase):
    def setUp(self):
        super(UserSectionTestCase, self).setUp()
        self.user = User.objects.create_user(username="fiera", email="fiera@votainteligente.cl", password="feroz")

    # This test should assert that a response redirects to the login interface
    # and if given a certain next_url then it also tests that
    # rigth after login it should go to that url
    def assertRedirectToLogin(self, response, next_url=None):
        self.assertEquals(response.status_code, 302)
        # when redirecting it always returns the full url based on test server so
        # in order to compare it I'll remove the testserver from the url
        location_this_response_is_taking_us_to = response['Location'].replace("http://testserver", "")
        # the login url comes with the localized url
        # So I'll set it to english and then remove it from the url
        activate('en')
        login_url = reverse('django.contrib.auth.views.login').replace('/en', '')
        self.assertTrue(location_this_response_is_taking_us_to.startswith(login_url))
        if next_url:
            current_domain = "http://" + Site.objects.get_current().domain
            next_url = next_url.replace(current_domain, "")
            self.assertTrue(location_this_response_is_taking_us_to.endswith("?next=" + next_url))

    # this code smels not nice
    # but it serves its porpouse for now if there is anyone that can improve it
    # feel free to do so


class UserViewTestCase(UserSectionTestCase):
    def test_account_url_exists(self):
        url = reverse('account')

        self.assertTrue(url)

    def test_the_url_is_not_reachable_when_not_logged(self):
        c = Client()
        url = reverse('account')
        response = c.get(url)
        self.assertRedirectToLogin(response, next_url=url)

    def test_the_url_exists_and_is_reachable_when_logged(self):
        c = Client()
        c.login(username='fiera', password='feroz')
        url = reverse('account')
        response = c.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "nuntium/profiles/your-profile.html")
        self.assertTemplateUsed(response, "base_edit.html")


class ContactsPerWriteItInstanceTestCase(UserSectionTestCase):
    def setUp(self):
        super(ContactsPerWriteItInstanceTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.get(id=1)
        self.writeitinstance.owner.set_password('feroz')
        self.writeitinstance.owner.save()

    def test_the_url_exists(self):
        '''The list of contacts per writeit instance exists'''
        url = reverse('contacts-per-writeitinstance', kwargs={'pk': self.writeitinstance.id})
        self.assertTrue(url)

    def test_the_url_is_reachable(self):
        '''The url is reachable'''
        url = reverse('contacts-per-writeitinstance', kwargs={'pk': self.writeitinstance.id})
        self.client.login(username=self.writeitinstance.owner, password="feroz")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'nuntium/profiles/contacts/contacts-per-writeitinstance.html')
        self.assertIn('writeitinstance', response.context)

    def test_only_owner_can_access_the_url(self):
        '''Only owner can access the list of contacts per writeitinstance'''
        other_user = User.objects.create_user(username='hello', password='password')
        writeitinstance = WriteItInstance.objects.create(name=u"The name", owner=other_user)
        url = reverse('contacts-per-writeitinstance', kwargs={'pk': writeitinstance.id})
        self.client.login(username=self.writeitinstance.owner, password="feroz")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get_the_list_of_people_in_context(self):
        '''The list of people is in context'''
        url = reverse('contacts-per-writeitinstance', kwargs={'pk': self.writeitinstance.id})
        self.client.login(username=self.writeitinstance.owner, password="feroz")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('people', response.context)
        self.assertIsInstance(response.context['people'][0], Person)


class YourInstancesViewTestCase(UserSectionTestCase):
    def setUp(self):
        super(YourInstancesViewTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.all()[0]
        self.writeitinstance.owner = self.user
        self.writeitinstance.save()

    def test_url_is_reachable(self):
        url = reverse('your-instances')
        self.assertTrue(url)

    def test_it_brings_the_list_of_instances(self):
        url = reverse('your-instances')
        c = Client()
        c.login(username="fiera", password="feroz")
        response = c.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['object_list']), 1)
        self.assertEquals(response.context['object_list'][0], self.writeitinstance)
        self.assertTemplateUsed(response, 'nuntium/profiles/your-instances.html')

    def test_it_is_not_reachable_by_a_non_user(self):
        url = reverse('your-instances')
        client = Client()
        response = client.get(url)
        self.assertRedirectToLogin(response, next_url=url)


class WriteitInstanceAdvancedUpdateTestCase(UserSectionTestCase):
    def setUp(self):
        super(WriteitInstanceAdvancedUpdateTestCase, self).setUp()
        self.factory = RequestFactory()
        self.writeitinstance = WriteItInstance.objects.all()[0]
        self.owner = self.writeitinstance.owner
        self.pedro = Person.objects.get(name="Pedro")
        self.marcel = Person.objects.get(name="Marcel")
        self.data = {
            'moderation_needed_in_all_messages': 1,
            'allow_messages_using_form': 1,
            'rate_limiter': 3,
            'notify_owner_when_new_answer': 1,
            'autoconfirm_api_messages': 1,
            }

    def test_writeitinstance_basic_form(self):
        form = WriteItInstanceAdvancedUpdateForm()
        self.assertEquals(form._meta.model, WriteItInstanceConfig)
        self.assertNotIn("name", form.fields)
        self.assertNotIn("slug", form.fields)
        self.assertNotIn("persons", form.fields)
        self.assertIn("moderation_needed_in_all_messages", form.fields)
        self.assertNotIn("owner", form.fields)
        self.assertIn("allow_messages_using_form", form.fields)
        self.assertIn("rate_limiter", form.fields)
        self.assertIn("notify_owner_when_new_answer", form.fields)
        self.assertIn("autoconfirm_api_messages", form.fields)
        self.assertIn("testing_mode", form.fields)

    def test_writeitinstance_advanced_form_save(self):
        url = reverse('writeitinstance_advanced_update', kwargs={'slug': self.writeitinstance.slug})
        c = Client()
        c.login(username=self.owner.username, password='admin')
        response = c.post(url, data=self.data, follow=True)
        self.assertRedirects(response, url)
        writeitinstance = WriteItInstance.objects.get(id=self.writeitinstance.id)
        self.assertTrue(writeitinstance.config.moderation_needed_in_all_messages)
        self.assertEquals(writeitinstance.config.allow_messages_using_form, 1)
        self.assertEquals(writeitinstance.config.rate_limiter, 3)
        self.assertEquals(writeitinstance.config.notify_owner_when_new_answer, 1)
        self.assertEquals(writeitinstance.config.autoconfirm_api_messages, 1)

    def test_update_view_is_not_reachable_by_a_non_user(self):
        url = reverse('writeitinstance_advanced_update', kwargs={'slug': self.writeitinstance.slug})
        client = Client()
        response = client.get(url)
        self.assertRedirectToLogin(response, next_url=url)

    def test_when_a_non_owner_saves_it_does_not_get_200_status_code(self):
        # I think that this test is unnecesary but
        # it could be of some use in the future
        # I have no opinion on this =/
        fiera = User.objects.create_user(
            username="fierita",
            email="fiera@votainteligente.cl",
            password="feroz",
            )
        url = reverse('writeitinstance_advanced_update', kwargs={'slug': self.writeitinstance.slug})
        c = Client()
        c.login(username=fiera.username, password='feroz')

        response = c.post(url, data=self.data, follow=True)

        self.assertEquals(response.status_code, 404)

from nuntium.popit_api_instance import PopitApiInstance
import json


class WriteItInstancePullingDetailViewTestCase(UserSectionTestCase):
    def setUp(self):
        super(WriteItInstancePullingDetailViewTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.get(id=1)
        self.owner = self.writeitinstance.owner
        self.popit_api_instance = PopitApiInstance.objects.get(id=1)
        self.record = WriteitInstancePopitInstanceRecord.objects.get_or_create(
            writeitinstance=self.writeitinstance,
            popitapiinstance=self.popit_api_instance)

    def test_theres_a_url_to_check_whats_happening(self):
        '''There is a url to let the user know what's happening with her/his instance'''
        url = reverse('pulling_status', kwargs={'pk': self.writeitinstance.pk})
        self.assertTrue(url)

    def test_get_content(self):
        '''The content should be a JSON containing the current status of the procedure'''
        url = reverse('pulling_status', kwargs={'pk': self.writeitinstance.pk})
        c = Client()
        c.login(username=self.owner.username, password='admin')
        response = c.get(url)
        current_status = json.loads(response.content)
        self.assertEquals(current_status, {'nothing': 1, 'inprogress': 0, 'success': 0, 'error': 0})

    def test_it_can_only_be_accessed_by_the_owner(self):
        '''It can only be accessed by the owner'''
        url = reverse('pulling_status', kwargs={'pk': self.writeitinstance.pk})
        c = Client()
        fiera = User.objects.create_user(
            username="fierita",
            email="fiera@votainteligente.cl",
            password="feroz",
            )
        c.login(username=fiera.username, password='feroz')

        response = c.get(url)

        self.assertEquals(response.status_code, 404)

    def test_cannot_be_accessed_by_a_non_user(self):
        '''It cannot be accessed by a non user'''
        url = reverse('pulling_status', kwargs={'pk': self.writeitinstance.pk})
        c = Client()
        response = c.get(url)
        self.assertRedirectToLogin(response)


class WriteitInstanceUpdateTestCase(UserSectionTestCase):
    def setUp(self):
        super(WriteitInstanceUpdateTestCase, self).setUp()
        self.factory = RequestFactory()
        self.writeitinstance = WriteItInstance.objects.get(id=1)
        self.owner = self.writeitinstance.owner
        self.pedro = Person.objects.get(name="Pedro")
        self.marcel = Person.objects.get(name="Marcel")

    def test_writeit_instance_edit_url_exists(self):
        url = reverse('writeitinstance_basic_update', kwargs={'slug': self.writeitinstance.slug})

        self.assertTrue(url)

    def test_update_view_is_not_reachable_by_a_non_user(self):
        url = reverse('writeitinstance_basic_update', kwargs={'pk': self.writeitinstance.pk})
        client = Client()
        response = client.get(url)
        self.assertRedirectToLogin(response, next_url=url)

    def test_writeitinstance_basic_form(self):
        form = WriteItInstanceBasicForm()
        self.assertEquals(form._meta.model, WriteItInstance)
        self.assertEquals(form._meta.fields, ['name'])

    def test_writeitinstance_basic_form_save(self):
        data = {
            'name': 'name 1'
            }
        url = reverse('writeitinstance_basic_update', kwargs={'pk': self.writeitinstance.pk})
        c = Client()
        c.login(username=self.owner.username, password='admin')

        response = c.post(url, data=data, follow=True)

        # self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, url)

        writeitinstance = WriteItInstance.objects.get(id=self.writeitinstance.id)
        self.assertEquals(writeitinstance.name, data['name'])

    def test_removing_a_person_from_writeitinstance_basic_form_save(self):
        data = {
            'name': 'new name 1'
            }
        url = reverse('writeitinstance_basic_update', kwargs={'pk': self.writeitinstance.pk})
        c = Client()
        c.login(username=self.owner.username, password='admin')

        c.post(url, data=data, follow=True)

        writeitinstance = WriteItInstance.objects.get(id=self.writeitinstance.id)
        self.assertEquals(writeitinstance.name, 'new name 1')

    def test_when_a_non_owner_saves_it_does_not_get_200_status_code(self):
        # I think that this test is unnecesary but
        # it could be of some use in the future
        # I have no opinion on this =/
        fiera = User.objects.create_user(username="fierita", email="fiera@votainteligente.cl", password="feroz")
        data = {
            'name': 'name 1',
            'persons': [self.pedro.id, self.marcel.id],
            }
        url = reverse('writeitinstance_basic_update', kwargs={'pk': self.writeitinstance.pk})
        c = Client()
        c.login(username=fiera.username, password='feroz')

        response = c.post(url, data=data, follow=True)

        self.assertEquals(response.status_code, 404)

    def test_update_view(self):
        url = reverse('writeitinstance_basic_update', kwargs={'pk': self.writeitinstance.pk})
        request = self.factory.get(url)
        request.user = self.user

        view = WriteItInstanceUpdateView()
        form_class = view.get_form_class()

        self.assertEquals(view.template_name_suffix, '_update_form')
        self.assertEquals(form_class, WriteItInstanceBasicForm)

    def test_updating_is_not_reachable_by_a_non_owner(self):
        fiera = User.objects.create_user(username="fierita", email="fiera@votainteligente.cl", password="feroz")

        c = Client()
        c.login(username=fiera.username, password='feroz')

        url = reverse('writeitinstance_basic_update', kwargs={'pk': self.writeitinstance.pk})

        response = c.get(url)

        self.assertEquals(response.status_code, 404)

    def test_updating_templates_views(self):
        self.writeitinstance.owner.set_password("feroz")
        self.writeitinstance.owner.save()
        c = Client()
        c.login(username=self.writeitinstance.owner.get_username(), password='feroz')

        url = reverse('writeitinstance_template_update', kwargs={'pk': self.writeitinstance.pk})

        response = c.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'base_edit.html')
        self.assertTemplateUsed(response, 'nuntium/profiles/templates.html')
        self.assertIsInstance(response.context['new_answer_template_form'], NewAnswerNotificationTemplateForm)
        self.assertIsInstance(response.context['mailit_template_form'], MailitTemplateForm)
        confirmation_template_form = response.context['confirmation_template_form']
        self.assertIsInstance(confirmation_template_form, ConfirmationTemplateForm)
        mailit_template_form = response.context['mailit_template_form']
        self.assertEquals(mailit_template_form.instance, self.writeitinstance.mailit_template)
        form = response.context['new_answer_template_form']
        self.assertEquals(form.instance, self.writeitinstance.new_answer_notification_template)
        self.assertEquals(confirmation_template_form.writeitinstance, self.writeitinstance)
        self.assertEquals(confirmation_template_form.instance, self.writeitinstance.confirmationtemplate)
        non_user = Client()

        response2 = non_user.get(url)
        self.assertRedirectToLogin(response2, next_url=url)

        # Benito does not own the instance
        User.objects.create_user(username="benito", email="benito@votainteligente.cl", password="feroz")

        fiera_client = Client()
        fiera_client.login(username="benito", password="feroz")

        response = fiera_client.get(url)
        self.assertEquals(response.status_code, 404)


class WriteItInstanceApiDocsTestCase(UserSectionTestCase):
    def setUp(self):
        super(WriteItInstanceApiDocsTestCase, self).setUp()
        self.factory = RequestFactory()
        self.writeitinstance = WriteItInstance.objects.get(id=1)

    def test_per_instance_api_docs(self):
        url = reverse('writeitinstance_api_docs', kwargs={'pk': self.writeitinstance.pk})
        request = self.factory.get(url)
        request.user = self.writeitinstance.owner

        response = WriteItInstanceApiDocsView.as_view()(request, pk=self.writeitinstance.pk)
        self.assertContains(response, 'http://testserver/api/v1/message/?format=json&username=admin&api_key=')


class NewAnswerNotificationUpdateViewForm(UserSectionTestCase):
    def setUp(self):
        super(NewAnswerNotificationUpdateViewForm, self).setUp()
        self.factory = RequestFactory()
        self.writeitinstance = WriteItInstance.objects.all()[0]
        self.writeitinstance.owner = self.user
        self.writeitinstance.save()
        self.pedro = Person.objects.get(name="Pedro")
        self.marcel = Person.objects.get(name="Marcel")

    def test_update_template_form(self):
        data = {
            'template_html': self.writeitinstance.new_answer_notification_template.template_html,
            'template_text': self.writeitinstance.new_answer_notification_template.template_text,
            'subject_template': 'subject =)',
            }
        form = NewAnswerNotificationTemplateForm(data,
            writeitinstance=self.writeitinstance,
            instance=self.writeitinstance.new_answer_notification_template)
        self.assertTrue(form.is_valid())

        template = form.save()
        self.assertEquals(template.subject_template, data['subject_template'])

    def test_update_template_view(self):
        url = reverse('edit_new_answer_notification_template', kwargs={'pk': self.writeitinstance.id})

        self.assertTrue(url)

        c = Client()
        # OK THE USER AND PASSWORD ARE CORRECT BUT THEY ARE NOT EXPLICIT, CAN YOU PLEASE HELP ME FIND A WAY
        # TO MAKE IT So?!?!?
        c.login(username="fiera", password="feroz")

        data = {
            'template_html': self.writeitinstance.new_answer_notification_template.template_html,
            'template_text': self.writeitinstance.new_answer_notification_template.template_text,
            'subject_template': 'subject =)',
            }

        response = c.post(url, data=data)
        url = reverse('writeitinstance_template_update', kwargs={'pk': self.writeitinstance.pk})
        self.assertRedirects(response, url)

        # actual_subject = self.writeitinstance.new_answer_notification_template.subject_template

    def test_a_non_owner_cannot_update_a_template(self):
        User.objects.create_user(username="not_owner", password="secreto")

        url = reverse('edit_new_answer_notification_template', kwargs={'pk': self.writeitinstance.id})
        c = Client()
        # logging in as another person different to the owner
        c.login(username="not_owner", password="secreto")

        data = {
            'template_html': self.writeitinstance.new_answer_notification_template.template_html,
            'template_text': self.writeitinstance.new_answer_notification_template.template_text,
            'subject_template': 'subject =)',
            }

        response = c.post(url, data=data)

        self.assertEquals(response.status_code, 404)

    def test_login_required_to_do_this_kind_of_stuff(self):
        url = reverse('edit_new_answer_notification_template', kwargs={'pk': self.writeitinstance.id})
        c = Client()
        data = {
            'template_html': self.writeitinstance.new_answer_notification_template.template_html,
            'template_text': self.writeitinstance.new_answer_notification_template.template_text,
            'subject_template': 'subject =)',
            }

        response = c.post(url, data=data)
        self.assertRedirectToLogin(response)


class CreateUserSectionInstanceTestCase(UserSectionTestCase):
    def setUp(self):
        super(CreateUserSectionInstanceTestCase, self).setUp()
        self.user = User.objects.first()
        self.data = {
            "name": 'instance',
            "popit_url": settings.TEST_POPIT_API_URL,
            }

    def test_create_an_instance_form(self):
        '''Create an instance with a very simple form in the user interface'''

        form = WriteItInstanceCreateForm(data=self.data, owner=self.user)
        self.assertTrue(form)
        self.assertTrue(form.is_valid())
        # the following lines are probably a little too deep in the details
        # but this isn't very simple to workout
        attrs_for_name = form.fields['name'].widget.attrs
        self.assertIn('class', attrs_for_name)
        self.assertEquals(attrs_for_name['class'], 'form-control')
        # everything ok until now
        attrs_for_popit_url = form.fields['popit_url'].widget.attrs
        self.assertIn('class', attrs_for_popit_url)
        self.assertEquals(attrs_for_popit_url['class'], 'form-control')

    @skipUnless(settings.LOCAL_POPIT, "No local popit running")
    def test_save_the_instance_with_the_form(self):
        popit_load_data()
        form = WriteItInstanceCreateForm(data=self.data, owner=self.user)
        instance = form.save()
        self.assertTrue(instance)
        self.assertEquals(instance.name, "instance")
        self.assertEquals(instance.owner, self.user)
        self.assertTrue(instance.persons.all())

    @skipUnless(settings.LOCAL_POPIT, "No local popit running")
    def test_post_to_create_an_instance(self):
        popit_load_data()
        c = Client()
        c.login(username=self.user.username, password='admin')
        url = reverse('create_writeit_instance')
        self.assertTrue(url)

        response = c.post(url, data=self.data)
        instance = WriteItInstance.objects.get(Q(name='instance'), Q(owner=self.user))
        self.assertRedirects(response, reverse('writeitinstance_basic_update', kwargs={'pk': instance.pk}))
        self.assertTrue(instance.persons.all())

    def test_create_an_instance_get_not_logged(self):
        '''Create an instance get'''

        url = reverse('create_writeit_instance')
        c = Client()
        response = c.get(url)
        self.assertRedirectToLogin(response)

    def test_it_redirects_to_your_instances(self):
        '''When get to create an instance it redirects to your instances'''
        url = reverse('create_writeit_instance')
        c = Client()

        response = c.get(url)
        c.login(username=self.user.username, password='admin')

        response = c.get(url)
        your_instances_url = reverse('your-instances')
        self.assertRedirects(response, your_instances_url)

    def test_your_instances_carries_a_create_form(self):
        '''Your instances has a form for creating an instance'''
        your_instances_url = reverse('your-instances')
        c = Client()
        c.login(username=self.user.username, password='admin')

        response = c.get(your_instances_url)
        self.assertIn('new_instance_form', response.context)
        self.assertIsInstance(response.context['new_instance_form'], WriteItInstanceCreateForm)
