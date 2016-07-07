from subdomains.utils import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.test.client import RequestFactory
from popit.models import Person
from mailit.forms import MailitTemplateForm
from global_test_case import GlobalTestCase as TestCase, popit_load_data

from instance.models import WriteItInstance, WriteitInstancePopitInstanceRecord
from nuntium.user_section.views import WriteItInstanceUpdateView, WriteItInstanceApiDocsView
from nuntium.user_section.forms import WriteItInstanceBasicForm, \
    WriteItInstanceCreateForm, \
    NewAnswerNotificationTemplateForm, ConfirmationTemplateForm
from django.test.utils import override_settings
from urlparse import urlparse
from nuntium.popit_api_instance import PopitApiInstance
import json
from nuntium.user_section.views import WriteItInstanceCreateView


class UserSectionTestCase(TestCase):
    def setUp(self):
        super(UserSectionTestCase, self).setUp()
        self.user = User.objects.create_user(username="fiera", email="fiera@votainteligente.cl", password="feroz")

    # This test should assert that a response redirects to the login interface
    # and if given a certain next_url then it also tests that
    # rigth after login it should go to that url
    def assertRedirectToLogin(self, response, next_url=None):
        self.assertEquals(response.status_code, 302)
        parsed_uri = urlparse(response.url)

        self.assertIn(parsed_uri.path, reverse('django.contrib.auth.views.login'))


class UserViewTestCase(UserSectionTestCase):
    def test_account_url_exists(self):
        reverse('account')

    def test_the_url_is_not_reachable_when_not_logged(self):
        c = self.client
        url = reverse('account')
        response = c.get(url)
        self.assertRedirectToLogin(response, next_url=url)

    def test_the_url_exists_and_is_reachable_when_logged(self):
        c = self.client
        c.login(username='fiera', password='feroz')
        url = reverse('account')
        response = c.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "nuntium/profiles/your-profile.html")
        self.assertTemplateUsed(response, "base_manager.html")


class ContactsPerWriteItInstanceTestCase(UserSectionTestCase):
    def setUp(self):
        super(ContactsPerWriteItInstanceTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.get(id=1)
        self.writeitinstance.owner.set_password('feroz')
        self.writeitinstance.owner.save()

    def test_the_url_exists(self):
        '''The list of contacts per writeit instance exists'''
        reverse('contacts-per-writeitinstance', subdomain=self.writeitinstance.slug)

    def test_the_url_is_reachable(self):
        '''The url is reachable'''
        url = reverse('contacts-per-writeitinstance', subdomain=self.writeitinstance.slug)
        self.client.login(username=self.writeitinstance.owner, password="feroz")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'nuntium/profiles/contacts/contacts-per-writeitinstance.html')
        self.assertIn('writeitinstance', response.context)

    def test_only_owner_can_access_the_url(self):
        '''Only owner can access the list of contacts per writeitinstance'''
        other_user = User.objects.create_user(username='hello', password='password')
        writeitinstance = WriteItInstance.objects.create(name=u"The name", owner=other_user)
        url = reverse('contacts-per-writeitinstance', subdomain=writeitinstance.slug)
        self.client.login(username=self.writeitinstance.owner, password="feroz")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get_the_list_of_people_in_context(self):
        '''The list of people is in context'''
        url = reverse('contacts-per-writeitinstance', subdomain=self.writeitinstance.slug)
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
        reverse('your-instances')

    def test_it_brings_the_list_of_instances(self):
        url = reverse('your-instances')
        c = self.client
        c.login(username="fiera", password="feroz")
        response = c.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['object_list']), 1)
        self.assertEquals(response.context['object_list'][0], self.writeitinstance)
        self.assertTemplateUsed(response, 'nuntium/profiles/your-instances.html')

    def test_it_is_not_reachable_by_a_non_user(self):
        url = reverse('your-instances')
        client = self.client
        response = client.get(url)
        self.assertRedirectToLogin(response, next_url=url)


class WriteitInstanceAdvancedUpdateTestCase(UserSectionTestCase):
    def setUp(self):
        super(WriteitInstanceAdvancedUpdateTestCase, self).setUp()
        self.factory = RequestFactory()
        self.writeitinstance = WriteItInstance.objects.all()[0]
        self.owner = self.writeitinstance.owner

    def test_rate_limit_cannot_be_negative(self):
        url = reverse('writeitinstance_ratelimiter_update', subdomain=self.writeitinstance.slug)
        modified_data = {'rate_limiter': -1}
        self.client.login(username=self.owner.username, password='admin')
        response = self.client.post(url, data=modified_data, follow=True)
        self.assertTrue(response.context['form'].errors)
        self.assertTrue(response.context['form'].errors['rate_limiter'])

    def test_change_rate_limit(self):
        url = reverse('writeitinstance_ratelimiter_update', subdomain=self.writeitinstance.slug)
        modified_data = {'rate_limiter': 10}
        self.client.login(username=self.owner.username, password='admin')
        self.client.post(url, data=modified_data, follow=True)
        writeitinstance = WriteItInstance.objects.get(id=self.writeitinstance.id)
        self.assertEquals(writeitinstance.config.rate_limiter, 10)

    def test_turning_moderation_on(self):
        url = reverse('writeitinstance_moderation_update', subdomain=self.writeitinstance.slug)
        modified_data = {'moderation_needed_in_all_messages': 'on'}
        self.client.login(username=self.owner.username, password='admin')
        self.client.post(url, data=modified_data, follow=True)
        writeitinstance = WriteItInstance.objects.get(id=self.writeitinstance.id)
        self.assertTrue(writeitinstance.config.moderation_needed_in_all_messages)

    def test_turning_moderation_off(self):
        url = reverse('writeitinstance_moderation_update', subdomain=self.writeitinstance.slug)
        modified_data = {}
        self.client.login(username=self.owner.username, password='admin')
        self.client.post(url, data=modified_data, follow=True)
        writeitinstance = WriteItInstance.objects.get(id=self.writeitinstance.id)
        self.assertFalse(writeitinstance.config.moderation_needed_in_all_messages)

    def test_turning_answer_notification_on(self):
        url = reverse('writeitinstance_answernotification_update', subdomain=self.writeitinstance.slug)
        modified_data = {'notify_owner_when_new_answer': 'on'}
        self.client.login(username=self.owner.username, password='admin')
        self.client.post(url, data=modified_data, follow=True)
        writeitinstance = WriteItInstance.objects.get(id=self.writeitinstance.id)
        self.assertTrue(writeitinstance.config.notify_owner_when_new_answer)

    def test_turning_answer_notification_off(self):
        url = reverse('writeitinstance_answernotification_update', subdomain=self.writeitinstance.slug)
        modified_data = {}
        self.client.login(username=self.owner.username, password='admin')
        self.client.post(url, data=modified_data, follow=True)
        writeitinstance = WriteItInstance.objects.get(id=self.writeitinstance.id)
        self.assertFalse(writeitinstance.config.notify_owner_when_new_answer)

    def test_turning_web_based_on(self):
        url = reverse('writeitinstance_webbased_update', subdomain=self.writeitinstance.slug)
        modified_data = {'allow_messages_using_form': 'on'}
        self.client.login(username=self.owner.username, password='admin')
        self.client.post(url, data=modified_data, follow=True)
        writeitinstance = WriteItInstance.objects.get(id=self.writeitinstance.id)
        self.assertTrue(writeitinstance.config.allow_messages_using_form)

    def test_turning_web_based_off(self):
        url = reverse('writeitinstance_webbased_update', subdomain=self.writeitinstance.slug)
        modified_data = {}
        self.client.login(username=self.owner.username, password='admin')
        self.client.post(url, data=modified_data, follow=True)
        writeitinstance = WriteItInstance.objects.get(id=self.writeitinstance.id)
        self.assertFalse(writeitinstance.config.allow_messages_using_form)

    def test_turning_api_autoconfirm_on(self):
        url = reverse('writeitinstance_api_autoconfirm_update', subdomain=self.writeitinstance.slug)
        modified_data = {'autoconfirm_api_messages': 'on'}
        self.client.login(username=self.owner.username, password='admin')
        self.client.post(url, data=modified_data, follow=True)
        writeitinstance = WriteItInstance.objects.get(id=self.writeitinstance.id)
        self.assertTrue(writeitinstance.config.autoconfirm_api_messages)

    def test_turning_api_autoconfirm_off(self):
        url = reverse('writeitinstance_api_autoconfirm_update', subdomain=self.writeitinstance.slug)
        modified_data = {}
        self.client.login(username=self.owner.username, password='admin')
        self.client.post(url, data=modified_data, follow=True)
        writeitinstance = WriteItInstance.objects.get(id=self.writeitinstance.id)
        self.assertFalse(writeitinstance.config.autoconfirm_api_messages)

    def test_set_max_recipients_to_7(self):
        url = reverse('writeitinstance_maxrecipients_update', subdomain=self.writeitinstance.slug)
        modified_data = {'maximum_recipients': 7}
        self.client.login(username=self.owner.username, password='admin')
        self.client.post(url, data=modified_data, follow=True)
        writeitinstance = WriteItInstance.objects.get(id=self.writeitinstance.id)
        self.assertEquals(writeitinstance.config.maximum_recipients, 7)

    def test_set_max_recipients_to_1(self):
        url = reverse('writeitinstance_maxrecipients_update', subdomain=self.writeitinstance.slug)
        modified_data = {'maximum_recipients': 1}
        self.client.login(username=self.owner.username, password='admin')
        self.client.post(url, data=modified_data, follow=True)
        writeitinstance = WriteItInstance.objects.get(id=self.writeitinstance.id)
        self.assertEquals(writeitinstance.config.maximum_recipients, 1)

    def test_set_max_recipients_to_zero(self):
        url = reverse('writeitinstance_maxrecipients_update', subdomain=self.writeitinstance.slug)
        modified_data = {'maximum_recipients': 0}
        self.client.login(username=self.owner.username, password='admin')
        response = self.client.post(url, data=modified_data, follow=True)
        self.assertTrue(response.context['form'].errors)
        self.assertTrue(response.context['form'].errors['maximum_recipients'])

    @override_settings(OVERALL_MAX_RECIPIENTS=10)
    def test_max_recipients_cannot_rise_more_than_settings(self):
        url = reverse('writeitinstance_maxrecipients_update', subdomain=self.writeitinstance.slug)
        modified_data = {'maximum_recipients': 11}
        self.client.login(username=self.owner.username, password='admin')
        response = self.client.post(url, data=modified_data, follow=True)
        self.assertTrue(response.context['form'].errors)
        self.assertTrue(response.context['form'].errors['maximum_recipients'])


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
        reverse('pulling_status', subdomain=self.writeitinstance.slug)

    def test_get_content(self):
        '''The content should be a JSON containing the current status of the procedure'''
        url = reverse('pulling_status', subdomain=self.writeitinstance.slug)
        c = self.client
        c.login(username=self.owner.username, password='admin')
        response = c.get(url)
        current_status = json.loads(response.content)
        self.assertEquals(current_status, {'nothing': 1, 'inprogress': 0, 'success': 0, 'error': 0})

    def test_it_can_only_be_accessed_by_the_owner(self):
        '''It can only be accessed by the owner'''
        url = reverse('pulling_status', subdomain=self.writeitinstance.slug)
        c = self.client
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
        url = reverse('pulling_status', subdomain=self.writeitinstance.slug)
        c = self.client
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
        reverse('writeitinstance_basic_update', subdomain=self.writeitinstance.slug)

    def test_update_view_is_not_reachable_by_a_non_user(self):
        url = reverse('writeitinstance_basic_update', subdomain=self.writeitinstance.slug)
        client = self.client
        response = client.get(url)
        self.assertRedirectToLogin(response, next_url=url)

    def test_when_a_non_owner_saves_it_does_not_get_200_status_code(self):
        # I think that this test is unnecesary but
        # it could be of some use in the future
        # I have no opinion on this =/
        fiera = User.objects.create_user(username="fierita", email="fiera@votainteligente.cl", password="feroz")
        data = {
            'name': 'name 1',
            'persons': [self.pedro.id, self.marcel.id],
            }
        url = reverse('writeitinstance_basic_update', subdomain=self.writeitinstance.slug)
        c = self.client
        c.login(username=fiera.username, password='feroz')

        response = c.post(url, data=data, follow=True)

        self.assertEquals(response.status_code, 404)

    def test_update_view(self):
        url = reverse('writeitinstance_basic_update', subdomain=self.writeitinstance.slug)
        request = self.factory.get(url)
        request.user = self.user

        view = WriteItInstanceUpdateView()
        form_class = view.get_form_class()

        self.assertEquals(view.template_name_suffix, '_update_form')
        self.assertEquals(form_class, WriteItInstanceBasicForm)

    def test_updating_is_not_reachable_by_a_non_owner(self):
        fiera = User.objects.create_user(username="fierita", email="fiera@votainteligente.cl", password="feroz")

        c = self.client
        c.login(username=fiera.username, password='feroz')
        url = reverse('writeitinstance_basic_update', subdomain=self.writeitinstance.slug)

        response = c.get(url)

        self.assertEquals(response.status_code, 404)

    def test_updating_templates_views(self):
        self.writeitinstance.owner.set_password("feroz")
        self.writeitinstance.owner.save()
        c = self.client
        c.login(username=self.writeitinstance.owner.get_username(), password='feroz')

        url = reverse('writeitinstance_template_update', subdomain=self.writeitinstance.slug)

        response = c.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'base_manager.html')
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
        non_user = self.client_class()

        response2 = non_user.get(url)
        self.assertRedirectToLogin(response2, next_url=url)

        # Benito does not own the instance
        User.objects.create_user(username="benito", email="benito@votainteligente.cl", password="feroz")

        fiera_client = self.client
        fiera_client.login(username="benito", password="feroz")

        response = fiera_client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_change_description(self):
        data = {
            'name': 'new name',
            'description': 'new description',
            'language': 'cs',
            }
        url = reverse('writeitinstance_basic_update', subdomain=self.writeitinstance.slug)
        c = self.client
        c.login(username=self.owner.username, password='admin')
        response = c.post(url, data=data)
        self.assertRedirects(response, url)
        writeitinstance = WriteItInstance.objects.get(id=self.writeitinstance.id)
        self.assertEquals(writeitinstance.name, data['name'])
        self.assertEquals(writeitinstance.description, data['description'])
        self.assertEquals(writeitinstance.config.default_language, data['language'])


class WriteItInstanceApiDocsTestCase(UserSectionTestCase):
    def setUp(self):
        super(WriteItInstanceApiDocsTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.get(id=1)

    def test_per_instance_api_docs(self):
        url = reverse('writeitinstance_api_docs', subdomain=self.writeitinstance.slug)
        request = self.factory.get(url)
        request.user = self.writeitinstance.owner

        response = WriteItInstanceApiDocsView.as_view()(request, pk=self.writeitinstance.pk)
        self.assertContains(response, 'api/v1/message/?format=json&username=admin&api_key=')


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
        url = reverse('edit_new_answer_notification_template', subdomain=self.writeitinstance.slug)

        c = self.client
        # OK THE USER AND PASSWORD ARE CORRECT BUT THEY ARE NOT EXPLICIT, CAN YOU PLEASE HELP ME FIND A WAY
        # TO MAKE IT So?!?!?
        c.login(username="fiera", password="feroz")

        data = {
            'template_html': self.writeitinstance.new_answer_notification_template.template_html,
            'template_text': self.writeitinstance.new_answer_notification_template.template_text,
            'subject_template': 'subject =)',
            }

        response = c.post(url, data=data)
        url = reverse('writeitinstance_template_update', subdomain=self.writeitinstance.slug)
        self.assertRedirects(response, url)

    def test_a_non_owner_cannot_update_a_template(self):
        User.objects.create_user(username="not_owner", password="secreto")

        url = reverse('edit_new_answer_notification_template', subdomain=self.writeitinstance.slug)
        c = self.client
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
        url = reverse('edit_new_answer_notification_template', subdomain=self.writeitinstance.slug)
        c = self.client
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
            "slug": 'test-instance-slug',
            "popit_url": settings.TEST_POPIT_API_URL,
            }

    def test_create_an_instance_form(self):
        '''Create an instance with a very simple form in the user interface'''

        form = WriteItInstanceCreateForm(data=self.data, owner=self.user)
        self.assertTrue(form)
        self.assertTrue(form.is_valid())
        # the following lines are probably a little too deep in the details
        # but this isn't very simple to workout
        attrs_for_slug = form.fields['slug'].widget.attrs
        self.assertIn('class', attrs_for_slug)
        self.assertEquals(attrs_for_slug['class'], 'form-control')
        # everything ok until now
        attrs_for_popit_url = form.fields['popit_url'].widget.attrs
        self.assertIn('class', attrs_for_popit_url)
        self.assertEquals(attrs_for_popit_url['class'], 'form-control')

    @popit_load_data()
    def test_save_the_instance_with_the_form(self):
        form = WriteItInstanceCreateForm(data=self.data, owner=self.user)
        instance = form.save()
        self.assertTrue(instance)
        self.assertEquals(instance.name, "test-instance-slug")
        self.assertEquals(instance.owner, self.user)
        self.assertTrue(instance.persons.all())

    @popit_load_data()
    def test_post_to_create_an_instance(self):
        c = self.client
        c.login(username=self.user.username, password='admin')
        url = reverse('create_writeit_instance')

        response = c.post(url, data=self.data)
        instance = WriteItInstance.objects.get(slug='test-instance-slug', owner=self.user)
        self.assertRedirects(response, reverse('welcome', subdomain=instance.slug))
        self.assertTrue(instance.persons.all())

    def test_create_an_instance_get_not_logged(self):
        '''Create an instance get'''

        url = reverse('create_writeit_instance')
        c = self.client
        response = c.get(url)
        self.assertRedirectToLogin(response)

    def test_get_url(self):
        '''Get the url for creating a new instance (it doesn't redrect anywhere)'''
        url = reverse('create_writeit_instance')
        request = self.factory.get(url)
        request.user = self.user
        response = WriteItInstanceCreateView.as_view()(request)
        # print response.render()
        self.assertEquals(response.status_code, 200)

    def test_your_instances_carries_a_create_form(self):
        '''Your instances has a form for creating an instance'''
        your_instances_url = reverse('your-instances')
        c = self.client
        c.login(username=self.user.username, password='admin')

        response = c.get(your_instances_url)
        self.assertIn('new_instance_form', response.context)
        self.assertIsInstance(response.context['new_instance_form'], WriteItInstanceCreateForm)
