from django.test import TestCase
from django.core.management import call_command


class GlobalTestCase(TestCase):
	def setUp(self):
		call_command('loaddata', 'example_data', verbosity=0)
