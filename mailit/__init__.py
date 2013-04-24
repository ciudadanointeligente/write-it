from nuntium.plugins import OutputPlugin
from django.core.mail import send_mail
from contactos.models import ContactType


class MailChannel(OutputPlugin):
    name = 'mail-channel'
    title = 'Mail Channel'

    def get_contact_type(self):
        contact_type, created = ContactType.objects.get_or_create(label_name="Electronic Mail", name="e-mail")
        return contact_type

    contact_type = property(get_contact_type)

    def send(self, message):
        for outbound_message in message.outboundmessage_set.all():
            format = {
                'subject':message.subject,
                'content':message.content,
                'person':outbound_message.contact.person.name
            }
            try:
                subject = message.writeitinstance.mailit_template.subject_template % format
                content = message.writeitinstance.mailit_template.content_template % format

                send_mail(subject, content, 'from@example.com',['to@example.com'], fail_silently=False)

            except:
                return False
            
        return True

