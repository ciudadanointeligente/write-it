
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

    def send(self, outbound_message):
        #Here there should be somewhere the contacts
        contact_type = self.contact_type

        try:
            template = outbound_message.message.writeitinstance.mailit_template

        except:
            return False, False

        format = {
            'subject':outbound_message.message.subject,
            'content':outbound_message.message.content,
            'person':outbound_message.contact.person.name,
            'author':outbound_message.message.author_name
        }
        subject = template.subject_template % format
        content = template.content_template % format

        #here there should be a try and except looking
        #for errors and stuff
        send_mail(subject, content, settings.DEFAULT_FROM_EMAIL,[outbound_message.contact.value], fail_silently=False)
            
        return (True,None)

