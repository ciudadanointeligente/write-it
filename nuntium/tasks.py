from celery import task
from .management.commands.send_mails import send_mails
from instance.models import WriteitInstancePopitInstanceRecord
from popolo_sources.models import PopoloSource
import logging


logger = logging.getLogger(__name__)


@task()
def send_mails_task():
    send_mails()


@task()
def pull_from_popolo_json(writeitinstance, popolo_source):
    result = writeitinstance._load_persons_from_popolo_json(popolo_source)
    logger.info(u'Resyncing {0} with {1}'.format(
        writeitinstance, popolo_source))
    return result


@task()
def update_all_instances(periodicity='1W'):
    all_records = WriteitInstancePopitInstanceRecord.objects.filter(periodicity=periodicity)
    logger.info(u'Complete resync of all instances')
    for record in all_records:
        popolo_source = PopoloSource.objects.get(id=record.popolo_source.id)
        pull_from_popolo_json(record.writeitinstance, popolo_source)
