from copy import copy
import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.db import models, transaction
from django.db.models import Prefetch
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from annoying.fields import AutoOneToOneField
from autoslug import AutoSlugField
from popolo.models import (
    Identifier as PopoloIdentifier,
    Person,
)
from popolo_sources.models import LinkToPopoloSource, PopoloSource
from popolo_sources.importer import PopoloSourceImporter
from requests.exceptions import ConnectionError
from subdomains.utils import reverse

from contactos.models import Contact
from mailit import MailChannel


class PopoloPersonQuerySet(models.QuerySet):

    def get_from_api_uri(self, uri_from_api):
        return self.get(
            identifiers__identifier=uri_from_api,
            identifiers__scheme__in=['popit_url', 'popolo_uri'])

    def origin(self, popolo_source):
        return self \
            .prefetch_related(Prefetch(
                'links_to_popolo_sources',
                LinkToPopoloSource.objects.select_related('popolo_source'))) \
            .filter(
                links_to_popolo_sources__popolo_source=popolo_source)

class PopoloPerson(Person):
    class Meta:
        proxy = True

    objects = PopoloPersonQuerySet.as_manager()

    links_to_popolo_sources = GenericRelation(
        LinkToPopoloSource,
        related_query_name='people')

    @classmethod
    def create_from_base_instance(cls, person):
        # Sometimes we have an instance of the base Person model, but
        # want the proxy model instance instead for its helper methods
        # or to add to a PopoloPerson relation. This seems like a
        # pretty horrible way to do it, but I don't know a neater way
        # to do this without something like
        # PopoloPerson.objects.get(pk=person.id) which would incur a
        # database query. http://stackoverflow.com/q/18473850/223092
        person = copy(person)
        person.__class__ = cls
        return person

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

    # This is actually only used in tests; associations with a
    # PopoloSource should all be handled by the update code in
    # multiple-django-popolo-sources.
    def add_link_to_popolo_source(self, popolo_source):
        ct = ContentType.objects.get_for_model(Person)
        LinkToPopoloSource.objects.get_or_create(
            popolo_source=popolo_source,
            content_type=ct,
            object_id=self.id)


def today_in_date_range(start_date, end_date):
    today = str(datetime.date.today())
    is_valid = ((not start_date) or str(start_date) <= today) and \
        ((not end_date) or str(end_date) >= today)
    return is_valid

def determine_if_person_is_current(person_object):
    return any(
        today_in_date_range(membership.start_date, membership.end_date)
        for membership in person_object.memberships.all()
    )

def create_contactos(person_object, writeitinstance):
    """Update Contact objects from contactos from the django-popolo Person"""

    # This replicates the logic from nuntium/popit_api_instance.py to
    # create these contacts, complete with its bugs, e.g. not removing
    # old Contacts that are no longer current (FIXME)
    contact_type = MailChannel().get_contact_type()
    created_emails = set()
    enable_contacts = determine_if_person_is_current(person_object)
    for contact_detail in person_object.contact_details.all():
        if contact_detail.contact_type == 'email':
            contact, created = Contact.objects.get_or_create(
                contact_type=contact_type,
                writeitinstance=writeitinstance,
                person=person_object)
            contact.value = contact_detail.value
            contact.enabled = enable_contacts
            contact.save()
            created_emails.add(contact.value)
    if person_object.email and person_object.email not in created_emails:
        contact, created = Contact.objects.get_or_create(
            contact_type=contact_type,
            writeitinstance=writeitinstance,
            person=person_object)
        contact.value = person_object.email
        contact.enabled = enable_contacts
        contact.save()


class ExtraIdentifierCreator(object):

    def __init__(self, popolo_source):
        self.popolo_source = popolo_source

    def notify(self, collection, django_object, created, popolo_data):
        if collection == 'person':
            uri = "{base_url}#{collection}-{popolo_id}".format(
                base_url=self.popolo_source.url,
                collection=collection,
                popolo_id=popolo_data['id'],
            )
            django_object.identifiers.create(
                scheme='popolo_uri',
                identifier=uri)

    def notify_deleted(self, collection, django_object):
        pass


class PersonTracker(object):

    def __init__(self):
        self.persons_present = set()
        self.persons_deleted = set()

    def notify(self, collection, django_object, created, popolo_data):
        if collection == 'person':
            self.persons_present.add(django_object)

    def notify_deleted(self, collection, django_object):
        if collection == 'person':
            self.persons_deleted.add(django_object)


class InstanceMembershipUpdater(object):

    def __init__(self, writeitinstance):
        self.writeitinstance = writeitinstance

    def notify(self, collection, django_object, created, popolo_data):
        # Make sure the InstanceMembership exists exactly once:
        if collection == 'person':
            self.writeitinstance.add_person(django_object)

    def notify_deleted(self, collection, django_object):
        # Make sure the InstanceMembership is removed:
        if collection == 'person':
            InstanceMembership.objects.filter(
                writeitinstance=self.writeitinstance,
                person_id=django_object.id)


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
        """Ensure there's exactly one link between the instance and a person"""

        # If we get given the base class rather than the proxy
        # class, we have to convert it before assigning it.
        if person._meta.model.__name__ == 'Person':
            person = PopoloPerson.create_from_base_instance(person)
        with transaction.atomic():
            # There might be multiple InstanceMembership relationships
            # between a particular person and instance, as a result of
            # an earlier bug (#429), so when adding make sure there's
            # only a single such InstanceMembership:
            kwargs = {'writeitinstance': self, 'person': person}
            existing = InstanceMembership.objects.filter(**kwargs)
            existing_count = existing.count()
            if existing_count == 0:
                InstanceMembership.objects.create(**kwargs)
            else:
                to_keep = existing.first()
                # Remove any extraneous additional InstanceMembership
                # objects:
                existing.exclude(pk=to_keep.id).delete()

    @property
    def persons_with_contacts(self):
        return self.persons.filter(contact__writeitinstance=self, contact__isnull=False).distinct()

    @property
    def has_popolo_memberships(self):
        return self.persons.filter(memberships__isnull=False).exists()

    def relate_with_persons_from_popolo_json(self, popolo_source):
        try:
            importer = PopoloSourceImporter(
                popolo_source,
                id_prefix='popolo:',
                truncate='yes',
                id_schemes_to_preserve={
                    'person': {'popit_id', 'popit_url',
                               'popit_django_person_id', 'popolo_uri'}
                })
            importer.add_observer(ExtraIdentifierCreator(popolo_source))
            importer.add_observer(InstanceMembershipUpdater(self))
            person_tracker = PersonTracker()
            importer.add_observer(person_tracker)
            importer.update_from_source()
            # Now update the contacts - note that we can't do this in
            # an observer, because when you're notified of updates to
            # a person their memberships won't be up to date yet - we
            # need to wait until the end.
            for person in person_tracker.persons_present:
                create_contactos(person, self)
            for person in person_tracker.persons_deleted:
                # Make sure any Contact objects for people who have been
                # deleted are disabled:
                Contact.objects.filter(
                    writeitinstance=self.writeitinstance,
                    person=person).update(enabled=False)
        except ConnectionError, e:
            self.do_something_with_a_vanished_popit_api_instance(popolo_source)
            e.message = _('We could not connect with the URL')
            return (False, e)
        except Exception, e:
            self.do_something_with_a_vanished_popit_api_instance(popolo_source)
            return (False, e)

        return (True, None)

    def do_something_with_a_vanished_popit_api_instance(self, popolo_source):
        pass

    def _load_persons_from_popolo_json(self, popolo_source):
        success_relating_people, error = self.relate_with_persons_from_popolo_json(popolo_source)
        record = WriteitInstancePopitInstanceRecord.objects.get(
            writeitinstance=self,
            popolo_source=popolo_source
            )
        if success_relating_people:
            record.set_status('success')
        else:
            if isinstance(error, ConnectionError):
                record.set_status('error', _('We could not connect with the URL'))
            else:
                record.set_status('error', error.message)
        return (success_relating_people, error)

    def load_persons_from_popolo_json(self, popolo_json_url):
        '''This is an async wrapper for getting people from the api'''
        popolo_source, created = PopoloSource.objects.get_or_create(url=popolo_json_url)
        record, created = WriteitInstancePopitInstanceRecord.objects.get_or_create(
            writeitinstance=self,
            popolo_source=popolo_source
            )
        if not created:
            record.updated = datetime.datetime.today()
            record.save()
        record.set_status('inprogress')
        from nuntium.tasks import pull_from_popolo_json
        return pull_from_popolo_json.delay(self, popolo_source)

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
