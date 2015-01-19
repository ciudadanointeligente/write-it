from celery import task
from .management.commands.send_mails import send_mails

@task()
def send_mails_task():
	send_mails()

@task()
def pull_from_popit(writeitinstance, popit_api_instance):
	result = writeitinstance.relate_with_persons_from_popit_api_instance(popit_api_instance)
	return result