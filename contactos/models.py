from django.db import models
from popit.models import Person
from django.utils.translation import ugettext as _
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
    value = models.CharField(max_length=512)
    is_bounced = models.BooleanField()
    owner = models.ForeignKey(User)

    def __unicode__(self):
    	return _('%(contact)s (%(type)s)') % {
	            'contact' : self.value,
	            'type' : self.contact_type.label_name
	        }



def notify_bounce(sender, instance, update_fields, **kwargs):
    contact = instance
    if contact.is_bounced:
        plaintext = get_template('contactos/mails/bounce_notification.txt')
        htmly     = get_template('contactos/mails/bounce_notification.html')

        context = Context({ 
            'contact':contact
             })

        text_content = plaintext.render(context)
        html_content = htmly.render(context)

        msg = EmailMultiAlternatives( _('Confirmation email for a message in WriteIt'), 
            text_content,#content
            settings.DEFAULT_FROM_EMAIL,#From
            [contact.owner.email]#To
            )
        msg.attach_alternative(html_content, "text/html")
        msg.send()


pre_save.connect(notify_bounce , sender=Contact)