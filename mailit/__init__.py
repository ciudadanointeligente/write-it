from nuntium.plugins import OutputPlugin
from django.core.mail import send_mail


class MailChannel(OutputPlugin):
    name = 'mail-channel'
    title = 'Mail Channel'

    def send(self, message):

        send_mail('Subject here', 'Here is the message.', 'from@example.com',['to@example.com'], fail_silently=False)
        return True

