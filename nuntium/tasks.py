from celery import task
from .management.commands.send_mails import send_mails
from instance.models import WriteitInstancePopitInstanceRecord
import logging


logger = logging.getLogger(__name__)


@task()
def send_mails_task():
    send_mails()


@task()
def pull_from_popit(writeitinstance, popit_api_instance):
    result = writeitinstance._load_persons_from_a_popit_api(popit_api_instance)
    logger.info(u'Resyncing ' + writeitinstance.__unicode__() + u' with ' + popit_api_instance.__unicode__())
    return result


@task()
def update_all_popits(periodicity='1W'):
    all_records = WriteitInstancePopitInstanceRecord.objects.filter(periodicity=periodicity)
    logger.info(u'Complete resync of all instances')
    for record in all_records:
        popit_api_instance = PopitApiInstance.objects.get(id=record.popitapiinstance.id)
        pull_from_popit(record.writeitinstance, popit_api_instance)
