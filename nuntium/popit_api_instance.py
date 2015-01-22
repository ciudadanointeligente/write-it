from popit.models import ApiInstance, Person, get_paginated_generator
from contactos.models import Contact
from mailit import MailChannel


class PopitPerson(Person):
    class Meta:
        proxy = True

    @classmethod
    def fetch_all_from_api(cls, instance, owner):
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
            PopitPerson.create_contact(obj, doc, owner)

    @classmethod
    def create_contact(self, obj, doc, owner):
        # obj.__class__ == nuntium.popit_api_instance.PopitPerson'

        for contact_detail in doc['contact_details']:
            if contact_detail['type'] == 'email':
                contact_type = MailChannel().get_contact_type()
                contact, created = Contact.objects.get_or_create(popit_identifier=contact_detail['id'],
                    contact_type=contact_type,
                    owner=owner,
                    person=obj)
                contact.value = contact_detail['value']
                contact.save()


class PopitApiInstance(ApiInstance):
    class Meta:
        proxy = True

    def fetch_all_from_api(self, owner):
        """
        Update all the local data from the API. This method actually delegates
        to the other models.
        """
        models = [PopitPerson]
        for model in models:
            model.fetch_all_from_api(instance=self, owner=owner)
