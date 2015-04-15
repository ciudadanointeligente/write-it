from popit.models import ApiInstance, Person, get_paginated_generator
from contactos.models import Contact
from mailit import MailChannel
from datetime import datetime
import slumber


def get_date_or_none(membership_doc, key, format="%Y-%m-%d"):
    date = membership_doc.get(key, "")
    if not date:
        return None
    try:
        return datetime.strptime(date, format)
    except TypeError:
        return None


def _is_current_membership(start_date, end_date):
    today = datetime.today()
    is_valid = ((start_date is None) or start_date <= today) and\
        ((end_date is None) or end_date >= today)
    return is_valid


def is_current_membership(membership_doc, start_date_key='start_date', end_date_key='end_date'):
    start_date = get_date_or_none(membership_doc, start_date_key)
    end_date = get_date_or_none(membership_doc, end_date_key)
    return _is_current_membership(start_date, end_date)


def get_about(url):
        try:
            api = slumber.API(url.replace('/v0.1', ''))
            response = api.about().get()
            return response.get('result', {})
        except slumber.exceptions.HttpClientError:
            return {}


class PopitPerson(Person):
    class Meta:
        proxy = True

    @classmethod
    def fetch_all_from_api(cls, instance, writeitinstance):
        """
        Get all the documents from the API and save them locally.
        """
        cls = Person
        api_client = instance.api_client(cls.api_collection_name)

        # This is hacky, but I can't see a documented way to get to the url.
        # Liable to change if slumber changes their internals.
        collection_url = api_client._store['base_url']

        for doc in get_paginated_generator(api_client):

            # Add url to the doc
            url = collection_url + '/' + doc['id']
            doc['popit_url'] = url

            obj = cls.update_from_api_results(instance=instance, doc=doc)
            PopitPerson.create_contact(obj, doc, writeitinstance)

    @classmethod
    def determine_if_person_is_current(cls, doc):
        enable = any([is_current_membership(membership) for membership in doc['memberships']])
        return enable

    @classmethod
    def create_contact(cls, obj, doc, writeitinstance):
        contact_type = MailChannel().get_contact_type()
        created_emails = []
        enable_contacts = cls.determine_if_person_is_current(doc)
        if 'contact_details' in doc:
            for contact_detail in doc['contact_details']:
                if contact_detail['type'] == 'email':
                    contact, created = Contact.objects.get_or_create(popit_identifier=contact_detail['id'],
                        contact_type=contact_type,
                        writeitinstance=writeitinstance,
                        person=obj)
                    contact.value = contact_detail['value']
                    contact.enabled = enable_contacts
                    contact.save()
                    created_emails.append(contact.value)
        if 'email' in doc and doc['email'] not in created_emails:
            contact, created = Contact.objects.get_or_create(
                contact_type=contact_type,
                writeitinstance=writeitinstance,
                person=obj)
            contact.value = doc['email']
            contact.enabled = enable_contacts
            contact.save()


class PopitApiInstance(ApiInstance):
    class Meta:
        proxy = True

    def fetch_all_from_api(self, writeitinstance):
        """
        Update all the local data from the API. This method actually delegates
        to the other models.
        """
        models = [PopitPerson]
        for model in models:
            model.fetch_all_from_api(instance=self, writeitinstance=writeitinstance)
