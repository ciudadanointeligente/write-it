import textwrap

from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.db import models
from django.utils.translation import override, ugettext_lazy as _
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from contactos.models import Contact
from .plugins import OutputPlugin
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import datetime
from djangoplugins.models import Plugin
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from subdomains.utils import reverse
import uuid
from django.template.defaultfilters import slugify
import re
from django.db.models import Q
import requests
from django.utils.timezone import now
from django.contrib.sites.models import Site

from unidecode import unidecode
from django.db.models.query import QuerySet
from itertools import chain
import os
import codecs

from instance.models import PopoloPerson, WriteItInstance
from writeit_utils import escape_dictionary_values


def read_template_as_string(path, file_source_path=__file__):
    script_dir = os.path.dirname(file_source_path)
    result = ''
    with codecs.open(os.path.join(script_dir, path), 'r', encoding='utf8') as f:
        result = f.read()
    return result


def template_with_wrap(template, context):
    wrapper = textwrap.TextWrapper(break_long_words=False, break_on_hyphens=False, replace_whitespace=False)
    return u'\n'.join(
        [wrapper.fill(x) for x in template.format(**context).splitlines()]
        )


class MessageRecord(models.Model):
    status = models.CharField(max_length=255)
    datetime = models.DateField(default=now)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        outbound_message = self.content_object
        return _('The message "%(subject)s" at %(instance)s'
           + ' turned %(status)s at %(date)s') % {
            'subject': outbound_message.message.subject,
            'instance': outbound_message.message.writeitinstance,
            'status': self.status,
            'date': str(self.datetime)
            }


class MessagesQuerySet(QuerySet):
    def filter(self, *args, **kwargs):
        person = None
        if 'person' in kwargs:
            person = kwargs.pop('person')

        queryset = super(MessagesQuerySet, self).filter(*args, **kwargs)
        if person:
            queryset = queryset.filter(
                Q(outboundmessage__contact__person=person) |
                Q(nocontactom__person=person)
                ).distinct()
        return queryset


class MessagesManager(models.Manager):
    def get_queryset(self):
        return MessagesQuerySet(self.model, using=self._db)


class PublicMessagesManager(MessagesManager):
    def get_queryset(self):
        queryset = super(PublicMessagesManager, self).get_queryset()
        return queryset.filter(Q(public=True), Q(confirmated=True),
            Q(moderated=True) | Q(moderated=None))


class NonModeratedMessagesManager(MessagesManager):
    def get_queryset(self):
        queryset = super(NonModeratedMessagesManager, self).get_queryset()
        return queryset.filter(Q(public=True), Q(confirmated=True))\
            .exclude(Q(moderated=True) | Q(moderated=None))


moderation_subject = read_template_as_string('templates/nuntium/mails/moderation_subject.txt').strip()
moderation_content_txt = read_template_as_string('templates/nuntium/mails/moderation_mail.txt')


class Message(models.Model):
    """Message: Class that contain the info for a model, \
    despite of the input and the output channels. Subject \
    and content are mandatory fields"""
    author_name = models.CharField(max_length=512, default='', blank=True)
    author_email = models.EmailField()
    subject = models.CharField(max_length=255)
    content = models.TextField()
    writeitinstance = models.ForeignKey(WriteItInstance)
    confirmated = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True)
    public = models.BooleanField(default=True)
    moderated = models.NullBooleanField()
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    objects = MessagesManager()
    public_objects = PublicMessagesManager()
    moderation_required_objects = NonModeratedMessagesManager()

    class Meta:
        ordering = ["-created"]

    def __init__(self, *args, **kwargs):
        self.persons = None
        if 'persons' in kwargs:
            self.persons = kwargs.pop('persons')

        super(Message, self).__init__(*args, **kwargs)

    def clean(self):
        try:
            rate_limiter = RateLimiter.objects.get(
                writeitinstance=self.writeitinstance,
                email=self.author_email,
                day=datetime.date.today()
                )
            if self.writeitinstance.config.rate_limiter > 0 and \
                    rate_limiter.count >= self.writeitinstance.config.rate_limiter:
                raise ValidationError(_('You have reached '
                    + 'your limit for today please try again tomorrow'))
        except ObjectDoesNotExist:
            pass
        super(Message, self).clean()

    #TODO: only new outbound_messages
    def recently_confirmated(self):
        status = 'ready'
        if not self.public or \
                self.writeitinstance.config.moderation_needed_in_all_messages:
            moderation, created = Moderation.objects.get_or_create(message=self)
            self.send_moderation_mail()
            status = 'needmodera'
        for outbound_message in self.outbound_messages:
            outbound_message.status = status
            outbound_message.save()

        if self.author_email:
            Subscriber.objects.create(email=self.author_email, message=self)
        self.confirmated = True
        self.save()

    @property
    def people(self):
        people = PopoloPerson.objects.filter(
            Q(contact__outboundmessage__message=self) |
            Q(nocontactom__message=self)
            ).distinct()

        return people

    @property
    def author_name_for_display(self):
        name = self.author_name
        if name == '':
            name = _('Anonymous')
        return name

    @property
    def outbound_messages(self):
        no_contact_oms = NoContactOM.objects.filter(message=self)
        outbound_messages = OutboundMessage.objects.filter(message=self)

        return list(chain(no_contact_oms, outbound_messages))

    def get_absolute_url(self):
        return reverse(
            'thread_read',
            subdomain=self.writeitinstance.slug,
            kwargs={
                'slug': self.slug,
                },
            )

    def slugifyme(self):
        if not slugify(unidecode(unicode(self.subject))):
            self.subject = '-'

        self.slug = slugify(unidecode(unicode(self.subject)))
        #Previously created messages with the same slug

        regex = "^" + self.slug + "(-[0-9]*){0,1}$"
        previously = Message.objects.filter(slug__regex=regex)
        count = 1
        for message in previously:
            new_regex = "^" + self.slug + "-(\d+){0,1}$"
            if re.match(new_regex, message.slug) is not None:
                groups = re.match(new_regex, message.slug).groups()
                if len(groups) > 0:
                    if int(groups[0]) > count:
                        count = int(groups[0])

        previously = previously.count()
        if previously > 0:
            self.slug = self.slug + '-' + str(count + 1)

    def veryfy_people(self):
        if not self.persons:
            raise TypeError(_('A message needs persons to be sent'))

    def create_moderation(self):
        Moderation.objects.create(message=self)

    def create_outbound_messages(self):
        if not self.persons:
            return
        for person in self.persons:
            self.create_outbound_messages_to_person(person)

    def create_outbound_messages_to_person(self, person):
        if not person.contact_set.all():
            NoContactOM.objects.get_or_create(message=self, person=person, site=Site.objects.get_current())
            return
        for contact in person.contact_set.filter(writeitinstance=self.writeitinstance):
            if not contact.is_bounced:
                OutboundMessage.objects.get_or_create(
                    contact=contact, message=self, site=Site.objects.get_current())

    def save(self, *args, **kwargs):
        created = self.id is None
        if created and self.writeitinstance.config.moderation_needed_in_all_messages:
            self.moderated = False
        super(Message, self).save(*args, **kwargs)
        if created and not self.public:
            self.create_moderation()
        self.create_outbound_messages()

    def set_to_ready(self):
        for outbound_message in self.outbound_messages:
            outbound_message.status = 'ready'
            outbound_message.save()

    def send_moderation_mail(self):
        url_reject = reverse('moderation_rejected',
            subdomain=self.writeitinstance.slug,
            kwargs={
                'slug': self.moderation.key
            })

        url_accept = reverse('moderation_accept',
            subdomain=self.writeitinstance.slug,
            kwargs={
                'slug': self.moderation.key
            })

        context = {
            'owner_name': self.writeitinstance.owner.username,
            'author_name': self.author_name_for_display,
            'author_email': self.author_email,
            'recipients': u', '.join([x.name for x in self.people]),
            'subject': self.subject,
            'content': self.content,
            'site_name': self.writeitinstance.name,
            'url_reject': url_reject,
            'url_accept': url_accept,
            }

        if settings.SEND_ALL_EMAILS_FROM_DEFAULT_FROM_EMAIL:
            from_email = settings.DEFAULT_FROM_EMAIL
        else:
            from_domain = self.writeitinstance.config.custom_from_domain\
                or settings.DEFAULT_FROM_DOMAIN
            from_email = self.writeitinstance.slug + "@" + from_domain

        connection = self.writeitinstance.config.get_mail_connection()
        msg = EmailMultiAlternatives(
            moderation_subject.format(**context),
            template_with_wrap(moderation_content_txt, context),
            from_email,
            [self.writeitinstance.owner.email],
            connection=connection,
            )
        msg.send()

    def moderate(self):
        if not self.confirmated:
            raise ValidationError(_('The message needs '
                + 'to be confirmated first'))
        self.set_to_ready()
        self.moderation.success()

    def __unicode__(self):
        return _('%(subject)s at %(instance)s') % {
            'subject': self.subject,
            'instance': self.writeitinstance.name,
            }


def slugify_message(sender, instance, **kwargs):
    created = instance.id is None
    if created:
        instance.slugifyme()
        instance.veryfy_people()

pre_save.connect(slugify_message, sender=Message)


class Answer(models.Model):
    content = models.TextField()
    content_html = models.TextField()
    person = models.ForeignKey(PopoloPerson)
    message = models.ForeignKey(Message, related_name='answers')
    created = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        memberships = self.message.writeitinstance.instancemembership_set.filter(person=self.person)
        if memberships.count() == 0:
            raise AttributeError(_("This guy does not belong here"))
        super(Answer, self).save(*args, **kwargs)

    def __unicode__(self):
        return _("%(person)s said \"%(content)s\""
                 + " to the message %(message)s") % {
            'person': self.person.name,
            'content': self.content,
            'message': self.message.subject,
            }


def send_new_answer_payload(sender, instance, created, **kwargs):
    answer = instance
    writeitinstance = answer.message.writeitinstance

    if created:
        connection = writeitinstance.config.get_mail_connection()
        new_answer_template = writeitinstance.new_answer_notification_template

        with override(None, deactivate=True):
            message_url = reverse('thread_read', subdomain=writeitinstance.slug, kwargs={'slug': answer.message.slug})

        context = {
            'author_name': answer.message.author_name_for_display,
            'person': answer.person.name,
            'subject': answer.message.subject,
            'content': answer.content,
            'message_url': message_url,
            'site_name': answer.message.writeitinstance.name,
            }

        subject = new_answer_template.get_subject_template().format(**context)
        text_content = new_answer_template.get_content_template().format(**context)
        html_content = new_answer_template.template_html.format(**escape_dictionary_values(context))

        if settings.SEND_ALL_EMAILS_FROM_DEFAULT_FROM_EMAIL:
            from_email = settings.DEFAULT_FROM_EMAIL
        else:
            from_domain = writeitinstance.config.custom_from_domain or settings.DEFAULT_FROM_DOMAIN
            from_email = "%s@%s" % (
                writeitinstance.slug,
                from_domain,
                )

        subscribers = answer.message.subscribers.all()

        if writeitinstance.config.notify_owner_when_new_answer:
            subscribers = chain(subscribers, (writeitinstance.owner,))

        for subscriber in subscribers:
            msg = EmailMultiAlternatives(
                subject.strip(),
                text_content,
                from_email,
                [subscriber.email],
                connection=connection,
                )
            if html_content:
                msg.attach_alternative(html_content, "text/html")
            msg.send()

        # Webhooks
        payload = {
            'message_id': '/api/v1/message/{0}/'.format(answer.message.id),
            'content': answer.content,
            'person': answer.person.name,
            'person_id': answer.person.uri_for_api(),
            'person_id_in_popolo_source': answer.person.id_in_popolo_source,
            'person_popolo_source_url': answer.person.popolo_source_url,
        }

        for webhook in writeitinstance.answer_webhooks.all():
            requests.post(webhook.url, data=payload)


post_save.connect(send_new_answer_payload, sender=Answer)


class AnswerAttachment(models.Model):
    answer = models.ForeignKey(Answer, related_name="attachments")
    content = models.FileField(upload_to="attachments/%Y/%m/%d")
    name = models.CharField(max_length=512, default="")


class OutboundMessageManager(models.Manager):
    def to_send(self, *args, **kwargs):
        query = super(OutboundMessageManager, self).filter(*args, **kwargs)
        return query.filter(status="ready")


class AbstractOutboundMessage(models.Model):
    STATUS_CHOICES = (
        ("new", _("Newly created")),
        ("ready", _("Ready to send")),
        ("sent", _("Sent")),
        ("error", _("Error sending it")),
        ("needmodera", _("Needs moderation")),
        )

    message = models.ForeignKey(Message)
    status = models.CharField(
        max_length="10",
        choices=STATUS_CHOICES,
        default="new",
        )
    site = models.ForeignKey(Site)

    class Meta:
        abstract = True


class NoContactOM(AbstractOutboundMessage):
    person = models.ForeignKey(PopoloPerson)


# This will happen everytime a contact is created

def create_new_outbound_messages_for_newly_created_contact(sender, instance, created, **kwargs):
    if kwargs['raw']:
        return

    contact = instance
    if not created:
        return
    writeitinstances = WriteItInstance.objects.filter(owner=contact.writeitinstance.owner)
    messages = Message.objects.filter(writeitinstance__in=writeitinstances)
    no_contact_oms = NoContactOM.objects.filter(
        message__in=messages,
        person=contact.person)
    # NOTE TO DEVELOPER:
    # now it is automatic that everytime a contact is created
    # the nocontact_om is deleted and we create outbound messages
    # but what if we let the user choose if they want or not that behaviour
    for no_contact_om in no_contact_oms:
        OutboundMessage.objects.create(
            contact=contact,
            message=no_contact_om.message,
            # here I should test that it also
            # copies the status
            status=no_contact_om.status,
            site=Site.objects.get_current(),
            )

    no_contact_oms.delete()
post_save.connect(create_new_outbound_messages_for_newly_created_contact, sender=Contact)


class OutboundMessage(AbstractOutboundMessage):
    """docstring for OutboundMessage: This class is \
    the message delivery unit. The OutboundMessage is \
    the one that will be tracked in order \
    to know the actual status of the message"""

    contact = models.ForeignKey(Contact)

    objects = OutboundMessageManager()

    def __unicode__(self):
        return _('%(subject)s sent to %(person)s '
                 + '(%(contact)s) at %(instance)s') % {
            'subject': self.message.subject,
            'person': self.contact.person.name,
            'contact': self.contact.value,
            'instance': self.message.writeitinstance.name,
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
        outbound_record, created = OutboundMessagePluginRecord.objects.get_or_create(
            outbound_message=self,
            plugin=plugin.get_model(),
            )
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
        # Also here comes what should be any priorization on the channels
        # that I'm not workin on right now and it should send to all of them
        # should I have another state "partly sent"? or
        # is it enough when I say "ready"?
        if sent_completely:
            self.status = "sent"
            self.save()
        MessageRecord.objects.create(content_object=self, status=self.status)


class OutboundMessageIdentifier(models.Model):
    outbound_message = models.OneToOneField(OutboundMessage)
    key = models.CharField(max_length=255)

    @classmethod
    def create_answer(cls, identifier_key, content, content_html=""):
        identifier = cls.objects.get(key=identifier_key)
        message = identifier.outbound_message.message
        person = identifier.outbound_message.contact.person
        popolo_person = PopoloPerson.create_from_base_instance(person)
        the_created_answer = Answer.objects.create(message=message,
            person=popolo_person,
            content=content,
            content_html=content_html)
        return the_created_answer

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = str(uuid.uuid1().hex)
        super(OutboundMessageIdentifier, self).save(*args, **kwargs)


def create_a_message_record(sender, instance, created, **kwargs):
    outbound_message = instance
    if created:
        MessageRecord.objects.create(
            content_object=outbound_message,
            status=outbound_message.status,
            )
        OutboundMessageIdentifier.objects.create(
            outbound_message=outbound_message)
post_save.connect(create_a_message_record, sender=OutboundMessage)


class OutboundMessagePluginRecord(models.Model):
    outbound_message = models.ForeignKey(OutboundMessage)
    plugin = models.ForeignKey(Plugin)
    sent = models.BooleanField(default=False)
    number_of_attempts = models.PositiveIntegerField(default=0)
    try_again = models.BooleanField(default=True)


default_confirmation_template_content_text = read_template_as_string('templates/nuntium/mails/confirmation/content_template.txt')
default_confirmation_template_subject = read_template_as_string('templates/nuntium/mails/confirmation/subject_template.txt')


class ConfirmationTemplate(models.Model):
    writeitinstance = models.OneToOneField(WriteItInstance)
    content_html = models.TextField(
        blank=True,
        help_text=_('You can use {author_name}, {site_name}, {subject}, {content}, {recipients}, {confirmation_url}, and {message_url}'),
        )
    content_text = models.TextField(
        blank=True,
        help_text=_('You can use {author_name}, {site_name}, {subject}, {content}, {recipients}, {confirmation_url}, and {message_url}'),
        )
    subject = models.CharField(
        max_length=512,
        blank=True,
        help_text=_('You can use {author_name}, {site_name}, {subject}, {content}, {recipients}, {confirmation_url}, and {message_url}'),
        )

    def get_content_template(self):
        return self.content_text or default_confirmation_template_content_text

    def get_subject_template(self):
        return self.subject or default_confirmation_template_subject


class Confirmation(models.Model):
    message = models.OneToOneField(Message)
    key = models.CharField(max_length=64, unique=True)
    created = models.DateField(default=now)
    confirmated_at = models.DateField(default=None, null=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = str(uuid.uuid1().hex)
        return super(Confirmation, self).save(*args, **kwargs)

    @property
    def is_confirmed(self):
        return self.confirmated_at is not None

    @classmethod
    def key_generator(cls):
        return str(uuid.uuid1().hex)

    def get_absolute_url(self):
        return reverse('confirm', subdomain=self.message.writeitinstance.slug, kwargs={'slug': self.key})


def send_confirmation_email(sender, instance, created, **kwargs):
    confirmation = instance
    if created:
        confirmation_url = reverse(
            'confirm',
            subdomain=confirmation.message.writeitinstance.slug,
            kwargs={'slug': confirmation.key},
        )
        message_full_url = confirmation.message.get_absolute_url()
        plaintext = confirmation.message.writeitinstance.confirmationtemplate.get_content_template()
        htmly = confirmation.message.writeitinstance.confirmationtemplate.content_html
        subject = confirmation.message.writeitinstance.confirmationtemplate.get_subject_template()
        subject = subject.rstrip()

        context = {
            'author_name': confirmation.message.author_name_for_display,
            'site_name': confirmation.message.writeitinstance.name,
            'subject': confirmation.message.subject,
            'content': confirmation.message.content,
            'recipients': u', '.join([x.name for x in confirmation.message.people]),
            'confirmation_url': confirmation_url,
            'message_url': message_full_url,
            }

        text_content = template_with_wrap(plaintext, context)
        subject = subject.format(**context)
        html_content = htmly.format(**escape_dictionary_values(context))

        if settings.SEND_ALL_EMAILS_FROM_DEFAULT_FROM_EMAIL:
            from_email = settings.DEFAULT_FROM_EMAIL
        else:
            from_domain = confirmation.message.writeitinstance.config.custom_from_domain\
                or settings.DEFAULT_FROM_DOMAIN
            from_email = "%s@%s" % (
                confirmation.message.writeitinstance.slug,
                from_domain,
                )
        connection = confirmation.message.writeitinstance.config.get_mail_connection()

        msg = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            [confirmation.message.author_email],
            connection=connection,
            )

        if html_content:
            msg.attach_alternative(html_content, "text/html")

        try:
            msg.send()
        except:
            pass


post_save.connect(send_confirmation_email, sender=Confirmation)


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
        return reverse('moderation_accept',
            subdomain=self.message.writeitinstance.slug,
            kwargs={
                'slug': self.key
            })

    def get_reject_url(self):
        return reverse('moderation_rejected',
            subdomain=self.message.writeitinstance.slug,
            kwargs={
                'slug': self.key
            })


class AnswerWebHook(models.Model):
    url = models.URLField(max_length=255)
    writeitinstance = models.ForeignKey(
        WriteItInstance,
        related_name='answer_webhooks',
        )

    def __unicode__(self):
        return '%(url)s at %(instance)s' % {
            'url': self.url,
            'instance': self.writeitinstance.name
        }


class Subscriber(models.Model):
    message = models.ForeignKey(Message, related_name='subscribers')
    email = models.EmailField()


default_new_answer_content_template = read_template_as_string('templates/nuntium/mails/new_answer.txt')
default_new_answer_subject_template = read_template_as_string('templates/nuntium/mails/nant_subject.txt')


class NewAnswerNotificationTemplate(models.Model):
    writeitinstance = models.OneToOneField(
        WriteItInstance,
        related_name='new_answer_notification_template',
        )
    template_html = models.TextField(
        blank=True,
        help_text=_('You can use {author_name}, {person}, {subject}, {content}, {message_url}, and {site_name}'),
        )
    template_text = models.TextField(
        blank=True,
        help_text=_('You can use {author_name}, {person}, {subject}, {content}, {message_url}, and {site_name}'),
        )
    subject_template = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('You can use {author_name}, {person}, {subject}, {content}, {message_url}, and {site_name}'),
        )

    def __unicode__(self):
        return _("Notification template for %s") % self.writeitinstance.name

    def get_content_template(self):
        return self.template_text or default_new_answer_content_template

    def get_subject_template(self):
        return self.subject_template or default_new_answer_subject_template


class RateLimiter(models.Model):
    writeitinstance = models.ForeignKey(WriteItInstance)
    email = models.EmailField()
    day = models.DateField()
    count = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        if not self.day:
            self.day = datetime.date.today()
        super(RateLimiter, self).save(*args, **kwargs)


def rate_limiting(sender, instance, created, **kwargs):

    if instance.author_email:
        rate_limiter, created = RateLimiter.objects.get_or_create(
            writeitinstance=instance.writeitinstance,
            email=instance.author_email,
            day=datetime.date.today()
            )
        if not created:
            rate_limiter.count = rate_limiter.count + 1
            rate_limiter.save()

post_save.connect(rate_limiting, sender=Message)

from tastypie.models import create_api_key

models.signals.post_save.connect(create_api_key, sender=User)
