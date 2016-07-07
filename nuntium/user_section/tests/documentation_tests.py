from global_test_case import GlobalTestCase as TestCase
from subdomains.utils import reverse
from instance.models import WriteItInstance


class DocumentationTestCase(TestCase):
    def setUp(self):
        super(DocumentationTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.all()[0]

    def test_I_can_access_the_docs(self):
        url = reverse('user_section_documentation')
        self.assertTrue(url)
        c = self.client
        c.login(username=self.writeitinstance.owner.username, password='admin')

        response = c.get(url)
        self.assertTemplateUsed(response, "nuntium/profiles/docs.html")
