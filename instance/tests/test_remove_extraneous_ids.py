from contextlib import contextmanager
import re
import sys

from django.core.management import call_command
from django.utils import six
from global_test_case import GlobalTestCase as TestCase

from instance.models import PopoloPerson
from popolo.models import Identifier


@contextmanager
def capture_output():
    # Suggested here: http://stackoverflow.com/a/17981937/223092
    new_out, new_err = six.StringIO(), six.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield new_out, new_err
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestRemoveExtraneousIDs(TestCase):

    def setUp(self):
        # Give everyone a popolo_uri Identifier:
        self.total_people = PopoloPerson.objects.count()
        for i, person in enumerate(PopoloPerson.objects.all()):
            identifier = 'https://example.com/foo.json#person-{0}'.format(i)
            person.identifiers.create(
                scheme='popolo_uri',
                identifier=identifier
            )

    def test_someone_with_no_popolo_uri(self):
        person_with_missing_id = PopoloPerson.objects.get(name='Felipe')
        person_with_missing_id.identifiers.filter(
            scheme='popolo_uri').delete()
        with capture_output() as (out, err):
            with self.assertRaises(Exception):
                call_command('instance_remove_extraneous_popolo_uri')
        self.assertEqual(
            out.getvalue(),
            'There were no popolo_uri Identifier objects for person Felipe with ID 3\n'
        )
        # Check that all the identifiers are still present,
        # i.e. nothing was deleted:
        self.assertEqual(
            Identifier.objects.filter(scheme='popolo_uri').count(),
            self.total_people - 1)

    def test_someone_with_only_a_bad_legacy_id(self):
        person_with_only_legacy_id = PopoloPerson.objects.get(name='Felipe')
        person_with_only_legacy_id.identifiers.filter(
            scheme='popolo_uri').delete()
        person_with_only_legacy_id.identifiers.create(
            scheme='popolo_uri',
            identifier='https://example.com/foo.json#person-person/42')
        with capture_output() as (out, err):
            with self.assertRaises(Exception):
                call_command('instance_remove_extraneous_popolo_uri')
        self.assertEqual(
            out.getvalue(),
            'The only remaining popolo_uri Identifier for person Felipe with ID 3 was a malformed legacy identifier: https://example.com/foo.json#person-person/42\n'
        )
        # Check that all the identifiers are still present,
        # i.e. nothing was deleted:
        self.assertEqual(
            Identifier.objects.filter(scheme='popolo_uri').count(),
            self.total_people)

    def test_conflicting_ids(self):
        person_with_only_legacy_id = PopoloPerson.objects.get(name='Felipe')
        person_with_only_legacy_id.identifiers.create(
            scheme='popolo_uri',
            identifier='https://example.com/foo.json#person-abcde')
        with capture_output() as (out, err):
            with self.assertRaises(Exception):
                call_command('instance_remove_extraneous_popolo_uri')
        self.assertEqual(
            out.getvalue(),
            '''There were multiple conflicting IDs for person Felipe with ID 3
  https://example.com/foo.json#person-2
  https://example.com/foo.json#person-abcde\n'''
        )
        # Check that all the identifiers are still present,
        # i.e. nothing was deleted:
        self.assertEqual(
            Identifier.objects.filter(scheme='popolo_uri').count(),
            self.total_people + 1)

    def test_normal_case(self):
        # Give everyone duplicate identifiers and a legacy one:
        for person in PopoloPerson.objects.all():
            identifier = person.identifiers.get(scheme='popolo_uri').identifier
            for _ in range(2):
                person.identifiers.create(
                    scheme='popolo_uri', identifier=identifier)
            i = re.search(r'person-([0-9]+)', identifier).group(1)
            fmt = 'https://example.com/foo.json#person-person/{0}'
            bad_identifier = fmt.format(i)
            person.identifiers.create(
                scheme='popolo_uri', identifier=bad_identifier)
        call_command('instance_remove_extraneous_popolo_uri')
        self.assertEqual(
            Identifier.objects.filter(scheme='popolo_uri').count(),
            self.total_people)
