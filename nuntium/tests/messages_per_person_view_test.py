# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from subdomains.utils import reverse, get_domain
from django.core.urlresolvers import reverse as original_reverse
from nuntium.models import WriteItInstance
from django.test.client import Client, RequestFactory
from nuntium.views import WriteItInstanceUpdateView
from django.contrib.sites.models import Site
from django.conf import settings
from popit.models import Person


class MessagesPerPersonViewTestCase(TestCase):
	def setUp(self):
		pass

	def test_has_an_url(self):
		writeitinstance = WriteItInstance.objects.get(id=1)
		pedro = Person.objects.get(id=1)
		url = reverse('messages_per_person'
			, kwargs={'pk':pedro.id}
            , subdomain=writeitinstance.slug)

		self.assertTrue(url)


