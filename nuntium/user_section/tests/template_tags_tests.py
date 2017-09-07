from django.template import Context, Template
from global_test_case import GlobalTestCase as TestCase
from contactos.models import Contact
from popolo.models import Person
from subdomains.utils import reverse
from django.template import TemplateSyntaxError


class ListContactsTemplateTag(TestCase):
    def setUp(self):
        super(ListContactsTemplateTag, self).setUp()
        self.contact = Contact.objects.get(id=1)

    def test_show_one_contact(self):
        '''When there is one contact it shows something {% show_contacts_for person writeitinstance %}'''
        t = Template('{% load nuntium_tags %}{% show_contacts_for person writeitinstance %}')
        c = Context({
            "person": self.contact.person,
            "writeitinstance": self.contact.writeitinstance
            })
        rendered = t.render(c)
        self.assertTrue(rendered)

    def test_it_shows_the_value_of_the_contact(self):
        '''It should show the contact value and the contact type'''
        t = Template('{% load nuntium_tags %}{% show_contacts_for person writeitinstance %}')
        c = Context({
            "person": self.contact.person,
            "writeitinstance": self.contact.writeitinstance
            })
        rendered = t.render(c)
        self.assertIn(self.contact.value, rendered)

    def test_join_with_commas(self):
        '''
        Join a list with commas
        '''
        t = Template('{% load nuntium_tags %}{{ people|join_with_commas }}')
        people = Person.objects.all().order_by('id')
        c = Context({
            "people": people
            })
        rendered = t.render(c)
        self.assertEquals(u'Pedro, Marcel and Felipe', rendered)

    def test_get_url_using_subdomain(self):
        '''
        There is a problem with the subdomain urls wich doesn't allow me to do the following
        '''

        with self.assertRaises(TemplateSyntaxError):
            t = Template("{% load subdomainurls %}{% url 'contact_us' subdomain=None as contact_page %}{{contact_page}}")
            t.render(Context({}))

        '''
        which is particularly useful when I want to include that url in the blocktrans
        tag as described in

        https://docs.djangoproject.com/en/1.6/topics/i18n/translation/#blocktrans-template-tag
        So I was thinking of creating another templatetag to do so.
        '''
        expected_template_rendered = reverse('contact_us', subdomain=None)

        t = Template("{% load nuntium_tags %}{% assignment_url_with_subdomain 'contact_us' subdomain=None as contact_page %}{{contact_page}}")
        actual_template_rendered = t.render(Context({}))

        self.assertEquals(expected_template_rendered, actual_template_rendered)
