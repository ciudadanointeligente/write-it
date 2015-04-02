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

    list_len = len(obj_list)
    if list_len == 0:
        return u""
    elif list_len == 1:
        return u"%s" % obj_list[0]
    else:
        return u", ".join(unicode(obj) for obj in obj_list[:list_len - 1]) + u" and " + unicode(obj_list[list_len - 1])

@register.simple_tag
def help_hint(help_url, help_target=""):
    if help_target:
        help_target = " data-target=\"%s\"" % help_target
    return "<a href=\"%s\" %sclass=\"help-loader\">[?]</a>" % (help_url, help_target)

