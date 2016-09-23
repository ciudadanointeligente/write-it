# -*- coding: utf-8 -*-

from datetime import datetime

from nuntium.templatetags.nuntium_tags import localize_datetime

from django.utils.translation import override

from django.template import Context, Template
from global_test_case import GlobalTestCase as TestCase


class DateLocalizationTests(TestCase):

    def setUp(self):
        self.dt = datetime(2015, 11, 28, 9, 45, 30)

    def test_tag_in_isolation_language_en(self):
        self.assertEqual(
            localize_datetime(self.dt, 'en'),
            self.dt)

    def test_tag_in_isolation_language_es(self):
        self.assertEqual(
            localize_datetime(self.dt, 'es'),
            self.dt)

    def test_tag_in_isolation_language_fa(self):
        self.assertEqual(
            localize_datetime(self.dt, 'fa'),
            u"شنبه ۷ آذر ۱۳۹۴ ۰۹:۴۵:۳۰ ق.ظ")

    def test_tag_in_template_language_en(self):
        template = Template('{% load nuntium_tags %}{{ dt|localize_datetime:"en" }}')
        with override('en'):
            self.assertEqual(
                template.render(Context({'dt': self.dt})),
                'Nov. 28, 2015, 9:45 a.m.')

    def test_tag_in_template_language_es(self):
        template = Template('{% load nuntium_tags %}{{ dt|localize_datetime:"es" }}')
        with override('es'):
            self.assertEqual(
                template.render(Context({'dt': self.dt})),
                '28 de Noviembre de 2015 a las 09:45')

    def test_tag_in_template_language_fa(self):
        template = Template('{% load nuntium_tags %}{{ dt|localize_datetime:"fa" }}')
        with override('fa'):
            self.assertEqual(
                template.render(Context({'dt': self.dt})),
                u'شنبه ۷ آذر ۱۳۹۴ ۰۹:۴۵:۳۰ ق.ظ')
