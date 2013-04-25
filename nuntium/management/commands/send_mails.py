from django.core.management.base import BaseCommand, CommandError
from nuntium.models import Message

class Command(BaseCommand):
    args = ''
    help = 'Sends all the available mails'

    def handle(self, *args, **options):
    	messages = Message.objects.to_send()
    	for message in messages:
    		message.send()