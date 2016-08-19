from collections import defaultdict
import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.db import models
from django.db.models.signals import post_save
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from annoying.fields import AutoOneToOneField
from autoslug import AutoSlugField
from popolo.models import (
    Membership as PopoloMembership,
    Organization as PopoloOrganization,
    Person,
)
import requests
from requests.exceptions import ConnectionError
from subdomains.utils import reverse

from contactos.models import Contact
from mailit import MailChannel


class PopoloPerson(Person):
    class Meta:
        proxy = True

    # Note that both these methods use the slightly odd implementation
    # of iterating over the relation rather than using .filter or .get
    # because if they're preloaded with prefetch_related those methods
    # will incur an extra query - .all will not.

    @property
    def popolo_source_url(self):
        result = None
        for ps in self.popolo_sources.all():
            # This assertion is because popolo_sources is a
            # many-to-many relationship, but in fact there can be no
            # more than one Popolo source that a Person is from.
            assert result is None
            result = ps
        return result

    @property
    def popolo_source_id(self):
        for i in self.identifiers.all():
            if i.scheme == 'popolo_source_id':
                return i.identifier

    @property
    def old_popit_url(self):
        # We shouldn't be relying on this any more, but are still
        # passing it in webhook payloads, so this property gives it an easy
        for i in self.identifiers.all():
            if i.scheme == 'popit_url':
                return i.identifier

# Big FIXME: all this syncing code is a crappier version of the popit
# import code in django-popolo - so we should just use that
# instead. This is a stop-gap measure (since the django-popolo
# importer needs a few changes to (a) handle inline memberships too
# and (b) we need to make sure it updates properly, removing removed
# memberships, etc. since so far it has mostly just been used for
# importing from scratch (c) we need to make sure it keeps all the
# data for different instances distinct.

def update_person(
        person_object,
        popolo_person_data,
        popolo_orgs,
        popolo_source_org_id_to_existing_org):
    """This updates the django-popolo Person from Popolo data"""

    # For the moment, just set the fields that the old popit-django
    # Person.extract_settable method would have; that's just 'name',
    # 'summary' and 'image':
    person_object['name'] = popolo_person_data.get('name', '')
    person_object['summary'] = popolo_person_data.get('summary', '')
    person_object['image'] = popolo_person_data.get('image', '')
    # However, also make sure that we update 'email', since that's
    # used for creating contacts:
    person_object['email'] = popolo_person_data.get('email', '')
    person_object.save()
    # Create the memberships too:
    person_object.membership.all.delete()
    for m in popolo_person_data['memberships']:
        m_org = popolo_orgs(m['organization_id'])
        org_object = popolo_source_org_id_to_existing_org.get(m_org['id'])
        if org_object is None:
            org_object = PopoloOrganization.objects.create(
                name=m_org['name']
            )
            org_object.identifiers.create(
                scheme='popolo_source_org_id',
                identifier=m_org['id'],
            )
        org_object.name = m_org['name']
        org_object.save()
        # Now we're sure that the person and organization exist, the
        # memberships can be created:
        PopoloMembership.objects.create(
            person=person_object,
            organization=org_object,
            start_date=m.get('start_date'),
            end_date=m.get('end_date'),
        )
    # Also, make sure the contacts are up-to-date:
    person_object.contact_set.all().delete()
    for contact_data in popolo_person_data['contact_details']:
        person_object.contact_set.create(
            contact_type=contact_data['type'],
            value=contact_data['value'],
        )

def today_in_date_range(start_date, end_date):
    today = datetime.today()
    is_valid = ((not start_date) or start_date <= today) and \
        ((not end_date) or end_date >= today)
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
    # old Contacts that are no longer current,
    contact_type = MailChannel().get_contact_type()
    created_emails = set()
    enable_contacts = determine_if_person_is_current(person_object)
    for contact_detail in person_object.contact_details.all():
        if contact_detail.contact_type == 'email':
            contact, created = Contact.objects.get_or_create(popit_identifier=contact_detail['id'],
                contact_type=contact_type,
                writeitinstance=writeitinstance,
                person=person_object)
            contact.value = contact_detail['value']
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


class PopoloSource(models.Model):
    url = models.URLField(max_length=255)
    persons = models.ManyToManyField(PopoloPerson, related_name='popolo_sources')

    def __unicode__(self):
        return self.url

    def get_popolo_data(self):
        people = {}
        r = requests.get(self.url)
        # These should all be single Popolo JSON file URLs after the
        # migration; the only subtlety is that some might have
        # 'memberships' inline in person objects, while in others you
        # have to look at a top-level 'memberships' array.
        data = r.json()
        organizations = {o['id']: o for o in data['organizations']}
        # Build a dictionary to map from person IDs to non-inline
        # memberships:
        person_id_to_memberships = defaultdict(list)
        for m in data['memberships']:
            p_id = m['person_id']
            person_id_to_memberships[p_id].append(m)
        # Now go through all the people:
        for p in data['persons']:
            extra_memberships = person_id_to_memberships[p['id']]
            # The old comment in nuntium/popit_api_instance.py was
            #   XXX IDs in transformed EP have person/ at the front?
            # So check whether there are memberships under that alternative
            # person ID:
            extra_memberships.extend(
                person_id_to_memberships['person/{0}'.format(p['id'])])
            p.setdefault('memberships', []).extend(extra_memberships)
            people[p['id']] = p
        return people, organizations

    def update_from_source(self, writeitinstance):
        with transaction.atomic():
            # Remove all old people associated with the
            # writeitinstance:
            writeitinstance.persons.clear()
            popolo_source_id_to_existing_person = {
                i.identifier: p
                for p in self.persons.all()
                for i in p.identifiers.all()
                if i.source == 'popolo_source_id'
            }
            popolo_source_org_id_to_existing_org = {
                i.identifier: o
                for o in PopoloOrganization.objects.all()
                for i in o.identifiers.all()
                if i.source == 'popolo_source_org_id'
            }
            # Get the Popolo person data with inline memberships:
            popolo_people, popolo_orgs = self.get_popolo_data()
            for popolo_person in popolo_people.values():
                person_object = popolo_source_id_to_existing_person.get(
                    popolo_person['id'])
                if person_object is not None:
                    # Create a minimal person and set the right identifier on
                    # them:
                    person_object = PopoloPerson.objects.create(
                        name=popolo_person['name']
                    )
                    person_object.identifiers.create(
                        scheme='popolo_source_id',
                        identifier=popolo_person['id'])
                # Now update the django-popolo Person and
                # ContactDetail objects:
                update_person(
                    person_object,
                    popolo_person,
                    popolo_orgs,
                    popolo_source_org_id_to_existing_org
                )
                writeitinstance.persons.add(person_object)
                # Finally make sure that the Contact objects from the
                # contactos apps are up-to-date:
                create_contactos(person_object, writeitinstance)


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

    def relate_with_persons_from_popolo_json(self, popolo_source):
        try:
            popolo_source.update_from_source(self)
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
