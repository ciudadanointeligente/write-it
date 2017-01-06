from django.core.management.base import BaseCommand
from django.db import transaction

from instance.models import PopoloPerson

BAD_SUBSTRING = '#person-person/'


class Command(BaseCommand):

    help = "Remove any extraneous Identifier objects with scheme 'popolo_uri'"

    @transaction.atomic
    def handle(self, *args, **options):
        errors_found = False
        for person in PopoloPerson.objects.all():
            qs = person.identifiers.filter(scheme='popolo_uri')
            original_count = qs.count()
            if original_count == 0:
                msg = "There were no popolo_uri Identifier objects for person " \
                      "{person} with ID {person_id}"
                print msg.format(person=person, person_id=person.id)
                errors_found = True
                continue
            if original_count == 1:
                sole_identifier = qs.first()
                if BAD_SUBSTRING in sole_identifier.identifier:
                    msg = "The only remaining popolo_uri Identifier for " \
                          "person {person} with ID {person_id} was a " \
                          "malformed legacy identifier: {bad_identifier}"
                    print msg.format(
                        person=person,
                        person_id=person.id,
                        bad_identifier=sole_identifier.identifier)
                    errors_found = True
                    continue
            # Otherwise we have more than one identifier. Delete any
            # of the bad legacy IDs:
            qs.filter(identifier__contains=BAD_SUBSTRING).delete()
            # Now all the remaining identifiers should be the same; if
            # they're not, that's an error.
            unique_remaining = set(qs.values_list('identifier', flat=True))
            if len(unique_remaining) > 1:
                msg = "There were multiple conflicting IDs for person " \
                      "{person} with ID {person_id}"
                print msg.format(person=person, person_id=person.id)
                for non_unique_id in sorted(unique_remaining):
                    print " ", non_unique_id
                errors_found = True
                continue
            # Now remove all but one of the identifiers:
            count = qs.count()
            for i in qs[:count - 1]:
                i.delete()
        if errors_found:
            raise Exception("Errors were found; not committing the transaction")
