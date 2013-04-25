
from nuntium.plugins import OutputPlugin
from django.core.mail import send_mail
from contactos.models import ContactType
from django.conf import settings


class MailChannel(OutputPlugin):
    name = 'mail-channel'
    title = 'Mail Channel'

    def get_contact_type(self):
        contact_type, created = ContactType.objects.get_or_create(label_name="Electronic Mail", name="e-mail")
        return contact_type

    contact_type = property(get_contact_type)

    def send(self, message):
        contact_type = self.contact_type

        try:
            template = message.writeitinstance.mailit_template
        except:
            return False

        outbound_messages = message.outboundmessage_set.filter(contact__contact_type=contact_type)
        for outbound_message in outbound_messages:
            format = {
                'subject':message.subject,
                'content':message.content,
                'person':outbound_message.contact.person.name
            }
            try:
                subject = template.subject_template % format
                content = template.content_template % format
                send_mail(subject, content, settings.DEFAULT_FROM_EMAIL,[outbound_message.contact.value], fail_silently=False)

            except:
                return False
            
        return True

