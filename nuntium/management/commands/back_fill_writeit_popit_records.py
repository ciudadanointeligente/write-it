from django.core.management.base import BaseCommand, CommandError
from popit.models import ApiInstance
from ...models import WriteitInstancePopitInstanceRecord
from django.contrib.auth.models import User

class WPBackfillRecords(object):
	@classmethod
	def back_fill_popit_records(cls, writeitinstance):
		persons_in_instance = writeitinstance.persons.all()
		api_instances = ApiInstance.objects.filter(person__in=persons_in_instance).distinct()
		for a in api_instances:
			WriteitInstancePopitInstanceRecord.objects.create(writeitinstance=writeitinstance, \
				popitapiinstance=a)

	@classmethod
	def back_fill_popit_records_per_user(cls, user):
		for instance in user.writeitinstances.all():
			cls.back_fill_popit_records(writeitinstance=instance)

class Command(BaseCommand):
    args = 'username'
    help = 'Relates writeit instances and popit instances in records so you can update them'

    def handle(self, *args, **options):
    	username = args[0]
    	user = User.objects.get(username=username)
    	WPBackfillRecords.back_fill_popit_records_per_user(user)
