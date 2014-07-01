from popit.models import ApiInstance
from ....models import WriteitInstancePopitInstanceRecord

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

