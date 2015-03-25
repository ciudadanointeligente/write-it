from django.test import TestCase

from nuntium.models import escape_dictionary_values


class EscapingTestCase(TestCase):
    def test_escape_html(self):
        d = {'foo': '<a>'}
        new_d = escape_dictionary_values(d)
        self.assertEqual(new_d['foo'], u'&lt;a&gt;')
