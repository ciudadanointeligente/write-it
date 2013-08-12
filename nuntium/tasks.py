from celery import task
from nuntium.management.commands.send_mails import send_mails

@task()
def send_mails_task():
	send_mails()