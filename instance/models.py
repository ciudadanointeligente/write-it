import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from annoying.fields import AutoOneToOneField
from autoslug import AutoSlugField
from popolo_sources.models import PopoloSource
from popolo.models import Person
from requests.exceptions import ConnectionError
from subdomains.utils import reverse


class PopoloPerson(Person):
    class Meta:
        proxy = True

    objects = PopoloPersonQuerySet.as_manager()

    links_to_popolo_sources = GenericRelation(
        LinkToPopoloSource,
        related_query_name='people')

    @property
    def popolo_source(self):
        ct = ContentType.objects.get_for_model(Person)
        link = LinkToPopoloSource.objects.get(
            content_type=ct, object_id=self.id)
        return link.popolo_source

    @property
    def popolo_source_url(self):
        return self.popolo_source.url

    # Note that these methods use the slightly odd implementation
    # of iterating over the relation rather than using .filter or .get
    # because if they're preloaded with prefetch_related those methods
    # will incur an extra query - .all will not.

    @property
    def id_in_popolo_source(self):
        for i in self.identifiers.all():
            if i.scheme == 'popolo:person':
                return i.identifier

    @property
    def old_popit_url(self):
        # We shouldn't be relying on this any more, but are still
        # passing it in webhook payloads, so this property gives it an easy
        for i in self.identifiers.all():
            if i.scheme == 'popit_url':
                return i.identifier

    @property
    def old_popit_id(self):
        # We shouldn't be relying on this any more either, but it's
        # used in tests and checks that old behaviour still works.
        for i in self.identifiers.all():
            if i.scheme == 'popit_id':
                return i.identifier

    def uri_for_api(self):
        """Return the URL the tastypie API uses to refer to this person"""

        old_url = None
        new_url = None
        for i in self.identifiers.all():
            # If the old identifier exists, use this so that the IDs
            # used in the API don't change.
            if i.scheme == 'popit_url':
                assert old_url is None
                old_url = i.identifier
            # For more recently created Person objects, popolo_uri is
            # the best single identifier to use in the API:
            elif i.scheme == 'popolo_uri':
                assert new_url is None
                new_url = i.identifier
        if old_url:
            return old_url
        if new_url:
            return new_url
        msg = "Could find no global identifier for PopoloPerson with ID {0}"
        raise PopoloIdentifier.DoesNotExist(msg.format(self.pk))


class WriteItInstance(models.Model):
    """WriteItInstance: Entity that groups messages and people
    for usability purposes. E.g. 'Candidates running for president'"""
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=512, blank=True)
    slug = AutoSlugField(populate_from='name', unique=True)
    persons = models.ManyToManyField(PopoloPerson,
        related_name='writeit_instances',
        through='InstanceMembership')
    owner = models.ForeignKey(User, related_name="writeitinstances")

    def add_person(self, person):
        InstanceMembership.objects.get_or_create(
            writeitinstance=self, person=person)

    @property
    def persons_with_contacts(self):
        return self.persons.filter(contact__writeitinstance=self, contact__isnull=False).distinct()

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
            memberships = InstanceMembership.objects.filter(writeitinstance=self, person=person)
            if memberships.count() == 0:
                InstanceMembership.objects.create(writeitinstance=self, person=person)
            if memberships.count() > 1:
                membership = memberships[0]
                memberships.exclude(id=membership.id).delete()

        return (True, None)

    def do_something_with_a_vanished_popit_api_instance(self, popit_api_instance):
        pass

    def _load_persons_from_a_popit_api(self, popit_api_instance):
        success_relating_people, error = self.relate_with_persons_from_popit_api_instance(popit_api_instance)
        record = WriteitInstancePopitInstanceRecord.objects.get(
            writeitinstance=self,
            popitapiinstance=popit_api_instance
            )
        if success_relating_people:
            record.set_status('success')
        else:
            if isinstance(error, ConnectionError):
                record.set_status('error', _('We could not connect with the URL'))
            else:
                record.set_status('error', error.message)
        return (success_relating_people, error)

    def load_persons_from_a_popit_api(self, popit_url):
        '''This is an async wrapper for getting people from the api'''
        popit_api_instance, created = PopitApiInstance.objects.get_or_create(url=popit_url)
        record, created = WriteitInstancePopitInstanceRecord.objects.get_or_create(
            writeitinstance=self,
            popitapiinstance=popit_api_instance
            )
        if not created:
            record.updated = datetime.datetime.today()
            record.save()
        record.set_status('inprogress')
        from nuntium.tasks import pull_from_popit
        return pull_from_popit.delay(self, popit_api_instance)

    def get_absolute_url(self):
        return reverse('instance_detail', subdomain=self.slug)

    @property
    def pulling_from_popit_status(self):
        records = WriteitInstancePopitInstanceRecord.objects.filter(writeitinstance=self)
        result = {'nothing': 0, 'inprogress': 0, 'success': 0, 'error': 0}
        for record in records:
            result[record.status] += 1
        return result

    @property
    def can_create_messages(self):
        if self.config.allow_messages_using_form and \
                self.contacts.exists():
            return True

        return False

    def __unicode__(self):
        return self.name


class InstanceMembership(models.Model):
    person = models.ForeignKey(PopoloPerson)
    writeitinstance = models.ForeignKey(WriteItInstance)


def new_write_it_instance(sender, instance, created, **kwargs):
    from nuntium.models import (
        NewAnswerNotificationTemplate, ConfirmationTemplate)
    if created:
        NewAnswerNotificationTemplate.objects.create(
            writeitinstance=instance
            )
        ConfirmationTemplate.objects.create(
            writeitinstance=instance
        )

post_save.connect(new_write_it_instance, sender=WriteItInstance)


PERIODICITY = (
    ('--', 'Never'),
    ('2D', 'Twice every Day'),
    ('1D', 'Daily'),
    ('1W', 'Weekly'),
)


class WriteitInstancePopitInstanceRecord(models.Model):
    STATUS_CHOICES = (
        ("nothing", _("Not doing anything now")),
        ("error", _("Error")),
        ("success", _("Success")),
        ("waiting", _("Waiting")),
        ("inprogress", _("In Progress")),
        )
    writeitinstance = models.ForeignKey(WriteItInstance)
    popolo_source = models.ForeignKey(PopoloSource)
    periodicity = models.CharField(
        max_length="2",
        choices=PERIODICITY,
        default='1W',
        )
    status = models.CharField(
        max_length="20",
        choices=STATUS_CHOICES,
        default="nothing",
        )
    status_explanation = models.TextField(default='')
    updated = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    def __unicode__(self):
        return "The people from {url} were loaded into {instance}".format(
            url=self.popolo_source.url,
            instance=self.writeitinstance.__unicode__(),
            )

    def set_status(self, status, explanation=''):
        self.status = status
        self.status_explanation = explanation
        self.save()


class WriteItInstanceConfig(models.Model):
    writeitinstance = AutoOneToOneField(WriteItInstance, related_name='config')
    testing_mode = models.BooleanField(default=True)
    moderation_needed_in_all_messages = models.BooleanField(
        help_text=_("Every message is going to \
        have a moderation mail"), default=False)
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

    custom_from_domain = models.CharField(max_length=512, null=True, blank=True)
    email_host = models.CharField(max_length=512, null=True, blank=True)
    email_host_password = models.CharField(max_length=512, null=True, blank=True)
    email_host_user = models.CharField(max_length=512, null=True, blank=True)
    email_port = models.IntegerField(null=True, blank=True)
    email_use_tls = models.NullBooleanField()
    email_use_ssl = models.NullBooleanField()
    can_create_answer = models.BooleanField(default=False, help_text="Can create an answer using the WebUI")
    maximum_recipients = models.PositiveIntegerField(default=5)
    default_language = models.CharField(max_length=10, choices=settings.LANGUAGES)

    def get_mail_connection(self):
        connection = mail.get_connection()
        if self.custom_from_domain:
            connection.host = self.email_host
            connection.password = self.email_host_password
            connection.username = self.email_host_user
            connection.port = self.email_port
            connection.use_tls = self.email_use_tls
        return connection
