from django.db import models
from popit.models import Person
from popolo.models import Person as PopoloPerson
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.template import Context
from django.template.loader import get_template
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


class ContactType(models.Model):
    """This class contain all contact types"""
    name = models.CharField(max_length=255)
    label_name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.label_name


class Contact(models.Model):
    """docstring for Contact"""
    contact_type = models.ForeignKey('ContactType')
    person = models.ForeignKey(Person)
    popolo_person = models.ForeignKey(PopoloPerson, null=True, blank=True)
    value = models.CharField(max_length=512)
    is_bounced = models.BooleanField(default=False)
    owner = models.ForeignKey(User, related_name="contacts", null=True)
    writeitinstance = models.ForeignKey('instance.WriteItInstance', related_name="contacts", null=True)
    popit_identifier = models.CharField(max_length=512, null=True)
    enabled = models.BooleanField(default=True)

    def __unicode__(self):
        return _('%(contact)s (%(type)s) for %(person)s') % {
            'contact': self.value,
            'type': self.contact_type.label_name,
            'person': self.person.name,
            }

    def set_outbound_messages_to_ready(self):
        for outbound_message in self.outboundmessage_set.all():
            outbound_message.status = 'ready'
            outbound_message.save()

    def resend_messages(self):
        self.is_bounced = False
        self.save()
        for outbound_message in self.outboundmessage_set.filter(status="error"):
            outbound_message.send()

    @classmethod
    def are_there_contacts_for(cls, person):
        if person.contact_set.exclude(is_bounced=True).exists():
            return True
        return False

    def save(self, *args, **kwargs):
        super(Contact, self).save(*args, **kwargs)


def notify_bounce(sender, instance, update_fields, **kwargs):
    contact = instance
    updating = instance.id is not None
    if updating:
        try:
            current_instance = Contact.objects.get(id=instance.id)
        except:
            return
        if not current_instance.is_bounced and instance.is_bounced:
            plaintext = get_template('contactos/mails/bounce_notification.txt')
            htmly = get_template('contactos/mails/bounce_notification.html')

            context = Context({'contact': contact})

            text_content = plaintext.render(context)
            html_content = htmly.render(context)

            subject = _('The contact %(contact)s for %(person)s has bounced') % {
                'contact': contact.value,
                'person': contact.person.name
                }
            msg = EmailMultiAlternatives(
                subject,
                text_content,  # content
                settings.DEFAULT_FROM_EMAIL,  # From
                [contact.writeitinstance.owner.email],  # To
                )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
pre_save.connect(notify_bounce, sender=Contact)
