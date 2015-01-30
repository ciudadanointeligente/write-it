from django.db.models.signals import post_save, pre_save
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from popit.models import Person, ApiInstance
from contactos.models import Contact
from .plugins import OutputPlugin
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
import datetime
from djangoplugins.models import Plugin
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template, get_template_from_string
from django.template import Context, Template
from django.conf import settings
from django.core.urlresolvers import reverse
import uuid
from django.template.defaultfilters import slugify
import re
from django.db.models import Q
import requests
from autoslug import AutoSlugField
from unidecode import unidecode
from django.db.models.query import QuerySet
from itertools import chain
from django.utils.timezone import now
import os
from popit_api_instance import PopitApiInstance
from requests.exceptions import ConnectionError


def read_template_as_string(path, file_source_path=__file__):
    script_dir = os.path.dirname(file_source_path)
    result = ''
    with open(os.path.join(script_dir, path), 'r') as f:
        result = f.read()

    return result


class WriteItInstance(models.Model):
    """WriteItInstance: Entity that groups messages and people
    for usability purposes. E.g. 'Candidates running for president'"""
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', unique=True)
    persons = models.ManyToManyField(Person,
        related_name='writeit_instances',
        through='Membership')
    moderation_needed_in_all_messages = models.BooleanField(
        help_text=_("Every message is going to \
        have a moderation mail"), default=False)
    owner = models.ForeignKey(User, related_name="writeitinstances")
    allow_messages_using_form = models.BooleanField(
        help_text=_("Allow the creation of new messages \
        using the web"), default=True)
    rate_limiter = models.IntegerField(default=0)
    notify_owner_when_new_answer = models.BooleanField(
        help_text=_("The owner of this instance \
        should be notified \
        when a new answer comes in"), default=False)
    autoconfirm_api_messages = models.BooleanField(
        help_text=_("Messages pushed to the api should \
            be confirmed automatically"), default=True)

    def relate_with_persons_from_popit_api_instance(self, popit_api_instance):
        try:
            popit_api_instance.fetch_all_from_api(writeitinstance=self)
        except ConnectionError, e:
            self.do_something_with_a_vanished_popit_api_instance(popit_api_instance)
            e.message = _('We could not connect with the URL')
            return (False, e)
        except Exception, e:
            self.do_something_with_a_vanished_popit_api_instance(popit_api_instance)
            return (False, e)
        persons = Person.objects.filter(api_instance=popit_api_instance)
        for person in persons:
            # There could be several memberships created.
            memberships = Membership.objects.filter(writeitinstance=self, person=person)
            if memberships.count() == 0:
                Membership.objects.create(writeitinstance=self, person=person)
            if memberships.count() > 1:
                membership = memberships[0]
                memberships.exclude(id=membership.id).delete()

        return (True, None)

    def do_something_with_a_vanished_popit_api_instance(self, popit_api_instance):
        pass

    def _load_persons_from_a_popit_api(self, popit_api_instance):
        record, created = WriteitInstancePopitInstanceRecord\
                    .objects.get_or_create(
                        writeitinstance=self,
                        popitapiinstance=popit_api_instance)
        if not created:
            record.updated = datetime.datetime.today()
            record.save()
        success_relating_people, error = self.relate_with_persons_from_popit_api_instance(popit_api_instance)
        return (success_relating_people, error)

    def load_persons_from_a_popit_api(self, popit_url):
        '''This is an async wrapper for getting people from the api'''
        api_instance, created = PopitApiInstance.objects.get_or_create(url=popit_url)
        from nuntium.tasks import pull_from_popit
        return pull_from_popit.delay(self, api_instance)

    def get_absolute_url(self):
        return reverse('instance_detail', kwargs={
            'slug': self.slug})

    def __unicode__(self):
        return self.name


def new_write_it_instance(sender, instance, created, **kwargs):
    if created:
        NewAnswerNotificationTemplate.objects.create(
            writeitinstance=instance
            )
        ConfirmationTemplate.objects.create(
            writeitinstance=instance
        )

post_save.connect(new_write_it_instance, sender=WriteItInstance)


class Membership(models.Model):
    person = models.ForeignKey(Person)
    writeitinstance = models.ForeignKey(WriteItInstance)


class MessageRecord(models.Model):
    status = models.CharField(max_length=255)
    datetime = models.DateField(default=now())
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

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
            queryset = queryset.filter(outboundmessage__contact__person=person)
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


class Message(models.Model):
    """Message: Class that contain the info for a model, \
    despite of the input and the output channels. Subject \
    and content are mandatory fields"""
    author_name = models.CharField(max_length=512)
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
            if self.writeitinstance.rate_limiter > 0 and \
                    rate_limiter.count >= self.writeitinstance.rate_limiter:
                raise ValidationError(_('You have reached '
                    + 'your limit for today please try again tomorrow'))
        except ObjectDoesNotExist:
            pass
        super(Message, self).clean()

    #TODO: only new outbound_messages
    def recently_confirmated(self):
        status = 'ready'
        if not self.public or \
                self.writeitinstance.moderation_needed_in_all_messages:
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
        people = Person.objects.filter(
            Q(contact__outboundmessage__message=self) |
            Q(nocontactom__message=self)
            ).distinct()

        return people

    @property
    def outbound_messages(self):
        no_contact_oms = NoContactOM.objects.filter(message=self)
        outbound_messages = OutboundMessage.objects.filter(message=self)

        return list(chain(no_contact_oms, outbound_messages))

    def get_absolute_url(self):
        return reverse(
            'message_detail',
            kwargs={
                'slug': self.slug,
                'instance_slug': self.writeitinstance.slug,
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
            NoContactOM.objects.get_or_create(message=self, person=person)
            return
        for contact in person.contact_set.filter(writeitinstance=self.writeitinstance):
            if not contact.is_bounced:
                OutboundMessage.objects.get_or_create(
                    contact=contact, message=self)

    def save(self, *args, **kwargs):
        created = self.id is None
        if created and self.writeitinstance.moderation_needed_in_all_messages:
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
        plaintext = get_template('nuntium/mails/moderation_mail.txt')
        htmly = get_template('nuntium/mails/moderation_mail.html')
        current_site = Site.objects.get_current()
        current_domain = 'http://' + current_site.domain
        url_rejected = current_domain + reverse('moderation_rejected', kwargs={
            'slug': self.moderation.key
            })

        url_accept = current_domain + reverse('moderation_accept', kwargs={
            'slug': self.moderation.key
            })

        d = Context(
            {'message': self,
             'url_rejected': url_rejected,
             'url_accept': url_accept,
             })

        text_content = plaintext.render(d)
        html_content = htmly.render(d)

        if settings.SEND_ALL_EMAILS_FROM_DEFAULT_FROM_EMAIL:
            from_email = settings.DEFAULT_FROM_EMAIL
        else:
            from_email = self.writeitinstance.slug + "@" + settings.DEFAULT_FROM_DOMAIN

        msg = EmailMultiAlternatives(_('Moderation required for\
         a message in WriteIt'),
            text_content,  # content
            from_email,  # From
            [self.writeitinstance.owner.email]  # To
            )
        msg.attach_alternative(html_content, "text/html")
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
    person = models.ForeignKey(Person)
    message = models.ForeignKey(Message, related_name='answers')
    created = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        memberships = self.message.writeitinstance.membership_set.filter(person=self.person)
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


# Possible values are: \n {{ user }} is the name of who
# created the message, \n {{ person }}
# is the person who this message was written to
# {{ message }} is the message that {{ person }} got
# in the first place, and {{ answer }} is what {{ person }} wrote back
def send_new_answer_payload(sender, instance, created, **kwargs):
    answer = instance
    if created:
        new_answer_template = answer.message.writeitinstance.new_answer_notification_template
        htmly = get_template_from_string(new_answer_template.template_html)
        texty = get_template_from_string(new_answer_template.template_text)
        if settings.SEND_ALL_EMAILS_FROM_DEFAULT_FROM_EMAIL:
            from_email = settings.DEFAULT_FROM_EMAIL
        else:
            from_email = "%s@%s" % (
                answer.message.writeitinstance.slug, settings.DEFAULT_FROM_DOMAIN)
        subject_template = new_answer_template.subject_template
        for subscriber in answer.message.subscribers.all():
            d = Context({
                'user': answer.message.author_name,
                'person': answer.person,
                'message': answer.message,
                'answer': answer,
            })
            html_content = htmly.render(d)
            txt_content = texty.render(d)
            subject = subject_template % {
                'person': answer.person.name,
                'message': answer.message.subject,
                }
            msg = EmailMultiAlternatives(
                subject, txt_content, from_email, [subscriber.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        if answer.message.writeitinstance.notify_owner_when_new_answer:
            d = Context({
                'user': answer.message.writeitinstance.owner,
                'person': answer.person,
                'message': answer.message,
                'answer': answer,
                })
            html_content = htmly.render(d)
            txt_content = texty.render(d)
            subject = subject_template % {
                'person': answer.message.writeitinstance.owner.username,
                'message': answer.message.subject,
                }
            msg = EmailMultiAlternatives(
                subject,
                txt_content,
                from_email,
                [answer.message.writeitinstance.owner.email],
                )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        for webhook in answer.message.writeitinstance.answer_webhooks.all():
            payload = {
                'message_id': '/api/v1/message/{0}/'.format(answer.message.id),
                'content': answer.content,
                'person': answer.person.name,
                'person_id': answer.person.popit_url,
                }
            requests.post(webhook.url, data=payload)


post_save.connect(send_new_answer_payload, sender=Answer)


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

    class Meta:
        abstract = True


class NoContactOM(AbstractOutboundMessage):
    person = models.ForeignKey(Person)


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
    def create_answer(cls, identifier_key, content):
        identifier = cls.objects.get(key=identifier_key)
        message = identifier.outbound_message.message
        person = identifier.outbound_message.contact.person
        the_created_answer = Answer.objects.create(message=message, person=person, content=content)
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


default_confirmation_template_content = read_template_as_string('templates/nuntium/mails/confirmation/content_template.html')

default_confirmation_template_content_text = read_template_as_string('templates/nuntium/mails/confirmation/content_template.txt')

default_confirmation_template_subject = read_template_as_string('templates/nuntium/mails/confirmation/subject_template.txt')


class ConfirmationTemplate(models.Model):
    writeitinstance = models.OneToOneField(WriteItInstance)
    content_html = models.TextField(default=default_confirmation_template_content)
    content_text = models.TextField(default=default_confirmation_template_content_text)
    subject = models.CharField(max_length=512, default=default_confirmation_template_subject)


class Confirmation(models.Model):
    message = models.OneToOneField(Message)
    key = models.CharField(max_length=64, unique=True)
    created = models.DateField(default=now())
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
        return reverse('confirm', kwargs={'slug': self.key})


def send_an_email_to_the_author(sender, instance, created, **kwargs):
    confirmation = instance
    if created:
        url = reverse('confirm', kwargs={
            'slug': confirmation.key
            })
        current_site = Site.objects.get_current()
        confirmation_full_url = "http://" + current_site.domain + url
        message_full_url = "http://" + current_site.domain + confirmation.message.get_absolute_url()
        plaintext = Template(confirmation.message.writeitinstance.confirmationtemplate.content_text)
        htmly = Template(confirmation.message.writeitinstance.confirmationtemplate.content_html)
        subject = confirmation.message.writeitinstance.confirmationtemplate.subject
        subject = subject.rstrip()

        d = Context(
            {'confirmation': confirmation,
             'confirmation_full_url': confirmation_full_url,
             'message_full_url': message_full_url,
             })

        text_content = plaintext.render(d)
        html_content = htmly.render(d)
        if settings.SEND_ALL_EMAILS_FROM_DEFAULT_FROM_EMAIL:
            from_email = settings.DEFAULT_FROM_EMAIL
        else:
            from_email = "%s@%s" % (
                confirmation.message.writeitinstance.slug,
                settings.DEFAULT_FROM_DOMAIN,
                )

        msg = EmailMultiAlternatives(
            subject,
            text_content,  # content
            from_email,  # From
            [confirmation.message.author_email],  # To
            )
        msg.attach_alternative(html_content, "text/html")
        try:
            msg.send()
        except:
            pass


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

nant_html = read_template_as_string('templates/nuntium/mails/new_answer.html')

nant_txt = read_template_as_string('templates/nuntium/mails/new_answer.txt')

nant_subject = read_template_as_string('templates/nuntium/mails/nant_subject.txt')


class NewAnswerNotificationTemplate(models.Model):
    writeitinstance = models.OneToOneField(
        WriteItInstance,
        related_name='new_answer_notification_template',
        )
    template_html = models.TextField(
        default=nant_html,
        help_text=_('You can use {{ user }}, {{ person }}, \
            {{ message.subject }} and {{ answer.content }}'),
        )
    template_text = models.TextField(
        default=nant_txt,
        help_text=_('You can use {{ user }}, {{ person }}, \
            {{ message.subject }} and {{ answer.content }}'),
        )
    subject_template = models.CharField(
        max_length=255,
        default=nant_subject,
        help_text=_('You can use %(message)s and %(person)s'),
        )

    def __unicode__(self):
        return _("Notification template for %s") % self.writeitinstance.name


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


class WriteitInstancePopitInstanceRecord(models.Model):
    STATUS_CHOICES = (
        ("nothing", _("Not doing anything now")),
        ("error", _("Error")),
        ("success", _("Success")),
        ("waiting", _("Waiting")),
        ("inprogress", _("In Progress")),
        )
    writeitinstance = models.ForeignKey(WriteItInstance)
    popitapiinstance = models.ForeignKey(ApiInstance)
    autosync = models.BooleanField(default=True)
    status = models.CharField(
        max_length="20",
        choices=STATUS_CHOICES,
        default="nothing",
        )
    status_explanation = models.TextField(default='')
    updated = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    def __unicode__(self):
        return "The people from {url} was loaded into {instance}".format(
            url=self.popitapiinstance.url,
            instance=self.writeitinstance.__unicode__(),
            )

    def set_status(self, status, explanation):
        self.status = status
        self.status_explanation = explanation
        self.save()
