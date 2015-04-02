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

@register.filter
def join_with_commas(obj_list):
    """Takes a list of objects and returns their unicode representations,
    seperated by commas and with 'and' between the penultimate and final items
    For example, for a list of fruit objects:
    [<Fruit: apples>,<Fruit: oranges>,<Fruit: pears>] -> 'apples, oranges and pears'
    """

    l = len(obj_list)
    if l == 0:
        return ""
    elif l == 1:
        return u"%s" % obj_list[0]
    else:
        return ", ".join(unicode(obj) for obj in obj_list[:l - 1]) \
                + " and " + unicode(obj_list[l - 1])
