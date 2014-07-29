
from nuntium.plugins import OutputPlugin
from contactos.models import ContactType
from django.conf import settings

import logging
from django.template import Context
from django.template.loader import get_template_from_string
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
            'author':outbound_message.message.author_name,
            'writeit_url': outbound_message.message.writeitinstance.get_absolute_url()
        }
        d = Context(format)
        mail_as_txt = get_template_from_string(template.content_template)
        mail_as_html = get_template_from_string(template.content_html_template)
        text_content = mail_as_txt.render(d)
        html_content = mail_as_html.render(d)


        subject = template.subject_template % format
        content = text_content
        author_name = outbound_message.message.author_name
        from_email = author_name + " <" + outbound_message.message.writeitinstance.slug+"+"+outbound_message.outboundmessageidentifier.key\
                                +'@'+settings.DEFAULT_FROM_DOMAIN + ">"

        #here there should be a try and except looking
        #for errors and stuff
        from django.core.mail.message import EmailMultiAlternatives
        try:
            msg = EmailMultiAlternatives(subject, content, from_email, [outbound_message.contact.value])
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)
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

        except Exception, e:
            log = "Error with outbound id %(outbound_id)i, contact '%(contact)s' and message '%(message)s' and the error was '%(error)s'"
            log = log % {
                'outbound_id':outbound_message.id,
                'contact':outbound_message.contact.value,
                'message':outbound_message.message,
                'error': e.__unicode__()
                }
            logging.info(log)
            return False, True
            
        return (True,None)

