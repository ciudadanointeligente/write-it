from celery import task
from .management.commands.send_mails import send_mails
from nuntium.models import WriteitInstancePopitInstanceRecord
from nuntium.popit_api_instance import PopitApiInstance


@task()
def send_mails_task():
    send_mails()


@task()
def pull_from_popit(writeitinstance, popit_api_instance):
    result = writeitinstance._load_persons_from_a_popit_api(popit_api_instance)
    return result


@task()
def update_all_popits():
    all_records = WriteitInstancePopitInstanceRecord.objects.all()

    for record in all_records:
        popit_api_instance = PopitApiInstance.objects.get(id=record.popitapiinstance.id)
        pull_from_popit(record.writeitinstance, popit_api_instance)
