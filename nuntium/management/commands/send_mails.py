from django.core.management.base import BaseCommand, CommandError
from nuntium.models import OutboundMessage

class Command(BaseCommand):
    args = ''
    help = 'Sends all the available mails'

    def handle(self, *args, **options):
    	outbound_messages = OutboundMessage.objects.to_send()
    	for outbound_message in outbound_messages:
    		outbound_message.send()