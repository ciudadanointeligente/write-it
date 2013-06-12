from django.db.models.signals import post_save
from django.db import models
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from popit.models import Person
from contactos.models import Contact
from nuntium.plugins import OutputPlugin
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
import datetime
from djangoplugins.models import Plugin
from django.core.mail import send_mail #Remove this when emailMultiAlternatives works
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
import uuid
from django.template.defaultfilters import slugify
import re
from django.contrib.auth.models import User
from django.contrib.sites.models import Site


class WriteItInstance(models.Model):
    """WriteItInstance: Entity that groups messages and people for usability purposes. E.g. 'Candidates running for president'"""
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    persons = models.ManyToManyField(Person, related_name='writeit_instances', through='Membership')
    owner = models.ForeignKey(User)

    @models.permalink
    def get_absolute_url(self):
        return ('instance_detail', (), {'slug': self.slug})

    def __unicode__(self):
        return self.name

class Membership(models.Model):
    person = models.ForeignKey(Person)
    writeitinstance = models.ForeignKey(WriteItInstance)

class MessageRecord(models.Model):
    status = models.CharField(max_length=255)
    datetime = models.DateField(default=datetime.datetime.now())
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        outbound_message = self.content_object
        return _('The message "%(subject)s" at %(instance)s turned %(status)s at %(date)s') % {
            'subject': outbound_message.message.subject,
            'instance': outbound_message.message.writeitinstance,
            'status': self.status,
            'date' : str(self.datetime)
            }


class Message(models.Model):
    """Message: Class that contain the info for a model, despite of the input and the output channels. Subject and content are mandatory fields"""
    author_name = models.CharField(max_length=512)
    author_email = models.EmailField()
    subject = models.CharField(max_length=512)
    content = models.TextField()
    writeitinstance = models.ForeignKey(WriteItInstance)
    slug = models.CharField(max_length=512)
    public = models.BooleanField(default=True)

    def __init__(self, *args, **kwargs):
        self.persons = None
        if 'persons' in kwargs:
            self.persons = kwargs.pop('persons')
        super(Message, self).__init__(*args, **kwargs)

    #TODO: only new outbound_messages
    def recently_confirmated(self):
        status = 'ready'
        if not self.public:
            self.send_moderation_mail()
            status = 'needmodera'
        for outbound_message in self.outboundmessage_set.all():
            outbound_message.status = status
            outbound_message.save()
        
    @property
    def people(self):
        people = []
        for outbound_message in self.outboundmessage_set.all():
            if outbound_message.contact.person not in people:
                people.append(outbound_message.contact.person)
        return people

    @models.permalink
    def get_absolute_url(self):
        return ('message_detail', (), {'slug': self.slug})

    def save(self, *args, **kwargs):

        created = self.id is None

        if created:
            self.slug = slugify(self.subject)
            #Previously created messages with the same slug
            previously = Message.objects.filter(subject=self.subject).count()
            if previously > 0:
                self.slug = self.slug + '-' + str(previously + 1)

            if not self.persons:
                raise TypeError(_('A message needs persons to be sent'))



        super(Message, self).save(*args, **kwargs)
        if created and not self.public:
            Moderation.objects.create(message=self)

        if self.persons:
            for person in self.persons:
                for contact in person.contact_set.all():
                    outbound_message = OutboundMessage.objects.get_or_create(contact=contact, message=self)



    def set_to_ready(self):
        for outbound_message in self.outboundmessage_set.all():
            outbound_message.status = 'ready'
            outbound_message.save()


    def send_moderation_mail(self):
        plaintext = get_template('nuntium/mails/moderation_mail.txt')
        htmly     = get_template('nuntium/mails/moderation_mail.html')
        current_site = Site.objects.get_current()
        current_domain = 'http://'+current_site.domain
        url_rejected = reverse('moderation_rejected', kwargs={
            'slug': self.moderation.key
            })
        url_rejected = current_domain+url_rejected
        url_accept = reverse('moderation_accept', kwargs={
            'slug': self.moderation.key
            })
        url_accept = current_domain+url_accept
        d = Context({ 
            'message': self,
            'url_rejected':url_rejected,
            'url_accept':url_accept
             })

        text_content = plaintext.render(d)
        html_content = htmly.render(d)

        msg = EmailMultiAlternatives( _('Confirmation email for a message in WriteIt'), 
            text_content,#content
            settings.DEFAULT_FROM_EMAIL,#From
            [self.writeitinstance.owner.email]#To
            )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def __unicode__(self):
        return _('%(subject)s at %(instance)s') % {
            'subject':self.subject,
            'instance':self.writeitinstance.name
            }

class Answer(models.Model):
    content = models.TextField()
    person = models.ForeignKey(Person)
    message = models.ForeignKey(Message, related_name='answers')
    created = models.DateField(default=datetime.datetime.now())

    def __init__(self, *args, **kwargs):
        super(Answer, self).__init__(*args, **kwargs)


    def save(self, *args, **kwargs):
        memberships = self.message.writeitinstance.membership_set.filter(person=self.person)
        if memberships.count() == 0:
            raise AttributeError(_("This guy does not belong here"))
        super(Answer, self).save(*args, **kwargs)




    def __unicode__(self):
        return _("%(person)s said \"%(content)s\" to the message %(message)s") % {
            'person': self.person.name,
            'content': "the answer to that is ...",
            'message': self.message.subject
            }


class OutboundMessageManager(models.Manager):
    def to_send(self, *args, **kwargs):
        query = super(OutboundMessageManager, self).filter(*args, **kwargs)
        return query.filter(status="ready")



class OutboundMessage(models.Model):
    """docstring for OutboundMessage: This class is the message delivery unit. The OutboundMessage is the one that will be tracked in order 
    to know the actual status of the message"""

    STATUS_CHOICES = (
        ("new",_("Newly created")),
        ("ready",_("Ready to send")),
        ("sent",_("Sent")),
        ("error",_("Error sending it")),
        ("needmodera",_("Needs moderation")),
        )

    contact = models.ForeignKey(Contact)
    message = models.ForeignKey(Message)
    status = models.CharField(max_length="10", choices=STATUS_CHOICES, default="new")

    objects = OutboundMessageManager()

    def __unicode__(self):
        return _('%(subject)s sent to %(person)s (%(contact)s) at %(instance)s') % {
            'subject': self.message.subject,
            'person':self.contact.person.name,
            'contact':self.contact.value,
            'instance':self.message.writeitinstance.name
        }
	
    def send(self):

        if self.status == "sent":
            return
        plugins = OutputPlugin.get_plugins()
        sent_completely = True

        #This is not the way it should be done
        #there should be some way to get the plugin from a contact_type
        outbound_message_plugin = None
        for plugin in plugins:
            if self.contact.contact_type == plugin.get_contact_type():
                outbound_message_plugin = plugin
                break
        outbound_record, created = OutboundMessagePluginRecord.objects.get_or_create(outbound_message=self, plugin=plugin.get_model())

        if not outbound_record.try_again:
            return

        if outbound_message_plugin is None:
            return

        successfully_sent, fatal_error = plugin.send(self)
        try_again = True
        if successfully_sent:
            try_again = False
        else:
            sent_completely = False
            if fatal_error:
                try_again = False
        outbound_record.sent = successfully_sent
        outbound_record.try_again = try_again
        outbound_record.number_of_attempts += 1
        outbound_record.save()
        #Also here comes what should be any priorization on the channels
        #that I'm not workin on right now and it should send to all of them
        #should I have another state "partly sent"? or is it enough when I say "ready"?
        if sent_completely:
            self.status = "sent"
            self.save()
        MessageRecord.objects.create(content_object= self, status=self.status)


def create_a_message_record(sender,instance, created, **kwargs):
    outbound_message = instance
    if created:
        MessageRecord.objects.create(content_object= outbound_message, status=outbound_message.status)
post_save.connect(create_a_message_record, sender=OutboundMessage)


class OutboundMessagePluginRecord(models.Model):
    outbound_message = models.ForeignKey(OutboundMessage)
    plugin = models.ForeignKey(Plugin)
    sent = models.BooleanField()
    number_of_attempts = models.PositiveIntegerField(default=0)
    try_again = models.BooleanField(default=True)


class Confirmation(models.Model):
    message = models.OneToOneField(Message)
    key = models.CharField(max_length=64, unique=True)
    created = models.DateField(default=datetime.datetime.now())
    confirmated_at = models.DateField(default=None, null=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = str(uuid.uuid1().hex)
        return super(Confirmation, self).save(*args, **kwargs)

    @property
    def is_confirmed(self):
        if self.confirmated_at is None:
            return False
        return True


    @classmethod
    def key_generator(cls):
        return str(uuid.uuid1().hex)



def send_an_email_to_the_author(sender,instance, created, **kwargs):
    confirmation = instance
    if created:
        url = reverse('confirm', kwargs={
            'slug':confirmation.key
            })
        current_site = Site.objects.get_current()
        confirmation_full_url = "http://"+current_site.domain+url
        message_full_url = 'http://'+current_site.domain+confirmation.message.get_absolute_url()

        plaintext = get_template('nuntium/mails/confirm.txt')
        htmly     = get_template('nuntium/mails/confirm.html')

        d = Context({ 'confirmation': confirmation, 
            'confirmation_full_url': confirmation_full_url,
            'message_full_url' : message_full_url
             })

        text_content = plaintext.render(d)
        html_content = htmly.render(d)

        msg = EmailMultiAlternatives( _('Confirmation email for a message in WriteIt'), 
            text_content,#content
            settings.DEFAULT_FROM_EMAIL,#From
            [confirmation.message.author_email]#To
            )
        msg.attach_alternative(html_content, "text/html")
        try:
            msg.send()
        except:
            confirmation.message.delete()


post_save.connect(send_an_email_to_the_author, sender=Confirmation)


class Moderation(models.Model):
    message = models.OneToOneField(Message, related_name='moderation')
    key = models.CharField(max_length=256)


    def save(self, *args, **kwargs):
        created = self.id is None
        if created:
            self.key = str(uuid.uuid1().hex)
        super(Moderation, self).save(*args, **kwargs)
        
