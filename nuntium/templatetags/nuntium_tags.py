from django import template
from contactos.models import Contact
from django.db.models import Q

register = template.Library()


def show_contacts_for(person, writeitinstance):
    contacts = Contact.objects.filter(Q(person=person), Q(writeitinstance=writeitinstance))
    return {
        "contacts": contacts,
        "person": person,
        "writeitinstance": writeitinstance
    }
register.inclusion_tag('nuntium/profiles/contacts/show_contacts_in.html')(show_contacts_for)
