from celery import task
from .management.commands.send_mails import send_mails


@task()
def send_mails_task():
    send_mails()


@task()
def pull_from_popit(writeitinstance, popit_api_instance):
    result = writeitinstance._load_persons_from_a_popit_api(popit_api_instance)
    return result
