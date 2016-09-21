import itertools
import logging
import textwrap

from django.conf import settings
from django.core.mail import mail_admins
from django.core.mail.message import EmailMultiAlternatives
from django.utils.translation import override

from smtplib import SMTPServerDisconnected, SMTPResponseException

from nuntium.plugins import OutputPlugin
from contactos.models import ContactType
from writeit_utils import escape_dictionary_values

logging.basicConfig(filename="send_mails.log", level=logging.INFO)


def process_content(content, indent='    ', width=66):
    """Take the provided message content. Wrap it at 66 characters, and then
    indent it by four spaces.
    """
    return u'\n'.join([indent + y
                       for y
                       in itertools.chain(*[lines or [u""] for lines in [textwrap.wrap(x, width) for x in content.splitlines()]])]
                      )


class MailChannel(OutputPlugin):
    name = 'mail-channel'
    title = 'Mail Channel'

    def get_contact_type(self):
        contact_type, created = ContactType.objects.get_or_create(label_name="Electronic Mail", name="e-mail")
        return contact_type

    contact_type = property(get_contact_type)

    def send(self, outbound_message):
        # Here there should be somewhere the contacts
        # Returns a tuple with the result_of_sending, fatal_error
        # so False, True means that there was an error sending and you should not try again
        try:
            writeitinstance = outbound_message.message.writeitinstance
            template = writeitinstance.mailit_template
        except:
            return False, False

        with override(writeitinstance.config.default_language):
            author_name = outbound_message.message.author_name
            context = {
                'subject': outbound_message.message.subject,
                'content': outbound_message.message.content,
                'content_indented': process_content(outbound_message.message.content),
                'person': outbound_message.contact.person.name,
                'author': author_name,
                'site_url': writeitinstance.get_absolute_url(),
                'message_url': outbound_message.message.get_absolute_url(),
                'site_name': writeitinstance.name,
                'owner_email': writeitinstance.owner.email,
                }
            try:
                text_content = template.get_content_template().format(**context)
                html_content = template.content_html_template.format(**escape_dictionary_values(context))
                subject = template.subject_template.format(**context)
            except KeyError, error:
                log = "Error with templates for instance %(instance)s and the error was '%(error)s'"
                log = log % {
                    'instance': writeitinstance.name,
                    'error': error.__unicode__()
                    }
                mail_admins("Problem sending an email", log)
                logging.info(log)
                return False, True

        if settings.SEND_ALL_EMAILS_FROM_DEFAULT_FROM_EMAIL:
            from_email = author_name + " <" + settings.DEFAULT_FROM_EMAIL + ">"
        else:
            from_domain = writeitinstance.config.custom_from_domain or settings.DEFAULT_FROM_DOMAIN
            from_email = (
                author_name + " <" + writeitinstance.slug +
                "+" + outbound_message.outboundmessageidentifier.key +
                '@' + from_domain + ">"
                )

        # There there should be a try and except looking
        # for errors and stuff
        try:
            to_email = writeitinstance.owner.email if writeitinstance.config.testing_mode else outbound_message.contact.value

            msg = EmailMultiAlternatives(
                subject,
                text_content,
                from_email,
                [to_email],
                connection=writeitinstance.config.get_mail_connection(),
                )
            if html_content:
                msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)
            log = "Mail sent from %(from)s to %(to)s"

            log = log % {
                'from': from_email,
                'to': outbound_message.contact.value,
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
                'outbound_id': outbound_message.id,
                'contact': outbound_message.contact.value,
                'message': outbound_message.message,
                'error': e.__unicode__()
                }
            mail_admins("Problem sending an email", log)
            logging.info(log)
            return False, True

        return True, None
