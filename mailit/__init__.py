
from nuntium.plugins import OutputPlugin
from django.core.mail import send_mail
from contactos.models import ContactType
from django.conf import settings
import logging
from smtplib import SMTPServerDisconnected, SMTPRecipientsRefused, SMTPResponseException

logging.basicConfig(filename="send_mails.log", level=logging.INFO)

class MailChannel(OutputPlugin):
    name = 'mail-channel'
    title = 'Mail Channel'

    def get_contact_type(self):
        contact_type, created = ContactType.objects.get_or_create(label_name="Electronic Mail", name="e-mail")
        return contact_type

    contact_type = property(get_contact_type)

    def send(self, outbound_message):
        #Here there should be somewhere the contacts
        #Returns a tuple with the result_of_sending, fatal_error
        # so False, True means that there was an error sending and you should not try again
        
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
        author_name = outbound_message.message.author_name
        from_email = author_name + " <" + outbound_message.message.writeitinstance.slug+"+"+outbound_message.outboundmessageidentifier.key\
                                +'@'+settings.DEFAULT_FROM_DOMAIN + ">"

        #here there should be a try and except looking
        #for errors and stuff
        from django.core.mail import send_mail
        try:
            send_mail(subject, content, from_email,[outbound_message.contact.value], fail_silently=False)
            log = "Mail sent from %(from)s to %(to)s"

            log = log % {
                'from':from_email,
                'to':outbound_message.contact.value
                }
            logging.info(log)
        except SMTPServerDisconnected, e:
            return False, False
        except SMTPResponseException, e:
            if e.smtp_code == 552:
                return False, False
            return False, True
            
        return (True,None)

