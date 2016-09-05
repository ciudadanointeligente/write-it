from django.core.management.base import BaseCommand
from instance.models import WriteitInstancePopitInstanceRecord
from popolo_sources.models import PopoloSource
from django.contrib.auth.models import User
import logging

logger = logging.getLogger('main')


class WPBackfillRecords(object):
    @classmethod
    def back_fill_popit_records(cls, writeitinstance):
        persons_in_instance = writeitinstance.persons.all()
        popolo_sources = PopoloSource.objects.filter(persons__in=persons_in_instance).distinct()
        for popolo_source in popolo_sources:
            record, created = WriteitInstancePopitInstanceRecord.objects.get_or_create(
                writeitinstance=writeitinstance,
                popolo_source=popolo_source)
            logger.info(
                u"Creating -> {record}\n".format(record=record.__unicode__()))

    @classmethod
    def back_fill_popit_records_per_user(cls, user):
        for instance in user.writeitinstances.all():
            cls.back_fill_popit_records(writeitinstance=instance)


class Command(BaseCommand, WPBackfillRecords):
    args = 'username'
    help = 'Relates writeit instances and popit instances in records so you can update them'

    def handle(self, *args, **options):
        try:
            username = args[0]
        except:
            logger.info("No username given\n")
            return
        try:
            user = User.objects.get(username=username)
        except:
            logger.info("User does not exist\n")
            return
        WPBackfillRecords.back_fill_popit_records_per_user(user)
