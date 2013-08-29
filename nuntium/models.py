from django.db.models.signals import post_save, pre_save
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
from django.utils.timezone import utc
from djangoplugins.models import Plugin
from django.core.mail import send_mail #Remove this when emailMultiAlternatives works
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template, get_template_from_string
from django.template import Context
from django.conf import settings
from subdomains.utils import reverse
from django.contrib.sites.models import Site
import uuid
from django.template.defaultfilters import slugify
import re
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import IntegrityError
from django.db.models import Q
import requests


class WriteItInstance(models.Model):
    """WriteItInstance: Entity that groups messages and people for usability purposes. E.g. 'Candidates running for president'"""
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    persons = models.ManyToManyField(Person, related_name='writeit_instances', through='Membership')
    moderation_needed_in_all_messages = models.BooleanField(help_text=_("Every message is going to have a moderation mail"))
    owner = models.ForeignKey(User)
    rate_limiter = models.IntegerField(default=0)

    
    def get_absolute_url(self):
        return reverse('instance_detail',subdomain=self.slug)

    def __unicode__(self):
        return self.name


def new_write_it_instance(sender,instance, created, **kwargs):
    if(created):
        new_answer_html = ''
        with open('nuntium/templates/nuntium/mails/new_answer.html', 'r') as f:
            new_answer_html += f.read()


        NewAnswerNotificationTemplate.objects.create(
            template = new_answer_html,
            writeitinstance=instance
            )

post_save.connect(new_write_it_instance, sender=WriteItInstance)


class Membership(models.Model):
    person = models.ForeignKey(Person)
    writeitinstance = models.ForeignKey(WriteItInstance)

class MessageRecord(models.Model):
    status = models.CharField(max_length=255)
    datetime = models.DateField(default=datetime.datetime.utcnow().replace(tzinfo=utc))
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

class PublicMessagesManager(models.Manager):
    def public(self,*args, **kwargs):
        query = super(PublicMessagesManager, self).filter(*args, **kwargs)
        query = query.filter(Q(public=True),Q(confirmated=True), Q(moderated=True)| Q(moderated=None))
        return query

class Message(models.Model):
    """Message: Class that contain the info for a model, despite of the input and the output channels. Subject and content are mandatory fields"""
    author_name = models.CharField(max_length=512)
    author_email = models.EmailField()
    subject = models.CharField(max_length=255)
    content = models.TextField()
    writeitinstance = models.ForeignKey(WriteItInstance)
    confirmated = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True)
    public = models.BooleanField(default=True)
    moderated = models.NullBooleanField()

    objects = PublicMessagesManager()

    def __init__(self, *args, **kwargs):
        self.persons = None
        if 'persons' in kwargs:
            self.persons = kwargs.pop('persons')

        super(Message, self).__init__(*args, **kwargs)


    #TODO: only new outbound_messages
    def recently_confirmated(self):
        status = 'ready'
        if not self.public or self.writeitinstance.moderation_needed_in_all_messages:
            moderation, created = Moderation.objects.get_or_create(message=self)
            self.send_moderation_mail()
            status = 'needmodera'
        for outbound_message in self.outboundmessage_set.all():
            outbound_message.status = status
            outbound_message.save()
        if self.author_email:
            Subscriber.objects.create(email=self.author_email, message=self)
            
        self.confirmated = True
        self.save()
        
    @property
    def people(self):
        people = []
        for outbound_message in self.outboundmessage_set.all():
            if outbound_message.contact.person not in people:
                people.append(outbound_message.contact.person)
        return people

    def get_absolute_url(self):
        return reverse('message_detail', subdomain=self.writeitinstance.slug, kwargs={'slug': self.slug})

    def slugifyme(self):
        self.slug = slugify(self.subject)
        #Previously created messages with the same slug
        
        regex = "^"+self.slug+"(-[0-9]*){0,1}$"
        previously = Message.objects.filter(slug__regex=regex)
        count = 1
        for message in previously:
            new_regex = "^"+self.slug+"-(\d+){0,1}$"
            if re.match(new_regex, message.slug) is not None:
                groups = re.match(new_regex, message.slug).groups()
                if len(groups) > 0:
                    if int(groups[0]) > count:
                        count = int(groups[0])
                    

        previously=previously.count()
        if previously > 0:
            self.slug = self.slug + '-' + str(count + 1)

    def veryfy_people(self):
        if not self.persons:
            raise TypeError(_('A message needs persons to be sent'))

    def create_moderation(self):
        Moderation.objects.create(message=self)

    def create_outbound_messages(self):
        if self.persons:
            for person in self.persons:
                for contact in person.contact_set.filter(owner=self.writeitinstance.owner):
                    if not contact.is_bounced:
                        outbound_message = OutboundMessage.objects.get_or_create(contact=contact, message=self)




    def save(self, *args, **kwargs):
        created = self.id is None
        if created and self.writeitinstance.moderation_needed_in_all_messages:
            self.moderated = False
        super(Message, self).save(*args, **kwargs)
        if created:
            if not self.public:
                self.create_moderation()
        self.create_outbound_messages()

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

        url_accept = reverse('moderation_accept', kwargs={
            'slug': self.moderation.key
            })

        d = Context({ 
            'message': self,
            'url_rejected':url_rejected,
            'url_accept':url_accept
             })

        text_content = plaintext.render(d)
        html_content = htmly.render(d)
        from_email = self.writeitinstance.slug+"@"+settings.DEFAULT_FROM_DOMAIN
        

        msg = EmailMultiAlternatives( _('Moderation required for a message in WriteIt'), 
            text_content,#content
            from_email,#From
            [self.writeitinstance.owner.email]#To
            )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def __unicode__(self):
        return _('%(subject)s at %(instance)s') % {
            'subject':self.subject,
            'instance':self.writeitinstance.name
            }


def slugify_message(sender,instance, **kwargs):
    created = instance.id is None
    if created:
        instance.slugifyme()
        instance.veryfy_people()

pre_save.connect(slugify_message, sender=Message)

class Answer(models.Model):
    content = models.TextField()
    person = models.ForeignKey(Person)
    message = models.ForeignKey(Message, related_name='answers')
    created = models.DateField(default=datetime.datetime.utcnow().replace(tzinfo=utc))

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
            'content': self.content,
            'message': self.message.subject
            }

subject_template = '%(person)s has answered to your message %(message)s'
def send_new_answer_payload(sender,instance, created, **kwargs):
    if created:
        for subscriber in instance.message.subscribers.all():
            new_answer_template = instance.message.writeitinstance.new_answer_notification_template
            htmly = get_template_from_string(new_answer_template.template)
            d = Context({ 
                'user': instance.message.author_name,
                'person':instance.person,
                'message':instance.message,
                'answer':instance
             })
            html_content = htmly.render(d)
            from_email = instance.message.writeitinstance.slug+"@"+settings.DEFAULT_FROM_DOMAIN
            subject = subject_template % {
            'person':instance.person.name,
            'message':instance.message.subject
            }
            send_mail(subject, html_content, from_email,[subscriber.email], fail_silently=False)


        for webhook in instance.message.writeitinstance.answer_webhooks.all():
            payload = {
                    'message_id':'/api/v1/message/{0}/'.format(instance.message.id),
                    'content': instance.content,
                    'person':instance.person.name
            }
            requests.post(webhook.url, data=payload)


post_save.connect(send_new_answer_payload, sender=Answer)



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

class OutboundMessageIdentifier(models.Model):
    outbound_message = models.OneToOneField(OutboundMessage)
    key = models.CharField(max_length = 255)

    @classmethod
    def create_answer(cls, identifier_key, content):
        identifier = cls.objects.get(key=identifier_key)
        message = identifier.outbound_message.message
        person = identifier.outbound_message.contact.person
        Answer.objects.create(message=message, person=person, content=content)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = str(uuid.uuid1().hex)
        super(OutboundMessageIdentifier, self).save(*args, **kwargs)


def create_a_message_record(sender,instance, created, **kwargs):
    outbound_message = instance
    if created:
        MessageRecord.objects.create(content_object= outbound_message, status=outbound_message.status)
        OutboundMessageIdentifier.objects.create(outbound_message=outbound_message)
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
    created = models.DateField(default=datetime.datetime.utcnow().replace(tzinfo=utc))
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

    def get_absolute_url(self):

        return reverse('confirm', kwargs={'slug': self.key})


def send_an_email_to_the_author(sender,instance, created, **kwargs):
    confirmation = instance
    if created:
        url = reverse('confirm', kwargs={
            'slug':confirmation.key
            })
        current_site = Site.objects.get_current()
        confirmation_full_url = url
        message_full_url = confirmation.message.get_absolute_url()
        plaintext = get_template('nuntium/mails/confirm.txt')
        htmly     = get_template('nuntium/mails/confirm.html')

        d = Context({ 'confirmation': confirmation, 
            'confirmation_full_url': confirmation_full_url,
            'message_full_url' : message_full_url
             })

        text_content = plaintext.render(d)
        html_content = htmly.render(d)
        from_email = confirmation.message.writeitinstance.slug+"@"+settings.DEFAULT_FROM_DOMAIN

        msg = EmailMultiAlternatives( _('Confirmation email for a message in WriteIt'), 
            text_content,#content
            from_email,#From
            [confirmation.message.author_email]#To
            )
        msg.attach_alternative(html_content, "text/html")
        try:
            msg.send()
        except:
            pass
            #confirmation.message.delete()


post_save.connect(send_an_email_to_the_author, sender=Confirmation)


class Moderation(models.Model):
    message = models.OneToOneField(Message, related_name='moderation')
    key = models.CharField(max_length=256)


    def save(self, *args, **kwargs):
        created = self.id is None
        if created:
            self.key = str(uuid.uuid1().hex)
        super(Moderation, self).save(*args, **kwargs)

    def success(self):
        self.message.moderated = True
        self.message.save()

    def get_success_url(self):
        return reverse('moderation_accept', kwargs={
            'slug': self.key
            })

    def get_reject_url(self):
        return reverse('moderation_rejected', kwargs={
            'slug': self.key
            })

class AnswerWebHook(models.Model):
    url = models.URLField(max_length=255)
    writeitinstance = models.ForeignKey(WriteItInstance, related_name='answer_webhooks')

    def __unicode__(self):
        return '%(url)s at %(instance)s'%{
            'url':self.url,
            'instance':self.writeitinstance.name
        }


class Subscriber(models.Model):
    message = models.ForeignKey(Message, related_name='subscribers')
    email = models.EmailField()

class NewAnswerNotificationTemplate(models.Model):
    writeitinstance = models.OneToOneField(WriteItInstance, related_name='new_answer_notification_template')
    template = models.TextField()
    subject_template = models.CharField(max_length=255, default=_('%(person)s has answered to your message %(message)s'))


class RateLimiter(models.Model):
    writeitinstance = models.ForeignKey(WriteItInstance)
    email = models.EmailField()
    day = models.DateField(auto_now=True)
    count = models.PositiveIntegerField(default=1)


def rate_limiting(sender,instance, created, **kwargs):
    if instance.author_email:
        RateLimiter.objects.create(writeitinstance=instance.writeitinstance, email=instance.author_email)

post_save.connect(rate_limiting, sender=Message)