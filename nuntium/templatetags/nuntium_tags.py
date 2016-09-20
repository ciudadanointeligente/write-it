import os
import re
from django import template
from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.utils.translation import ugettext_lazy as _
from django.contrib.staticfiles import finders
from contactos.models import Contact
from django.db.models import Q
from subdomains.templatetags.subdomainurls import url as subdomainsurls, UNSET
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
def join_with_commas(obj_list, language_code=None):
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
        if (language_code is None) or language_code.startswith('en'):
            return u", ".join(unicode(obj) for obj in obj_list[:list_len - 1]) + u" and " + unicode(obj_list[list_len - 1])
        else:
            return u", ".join(unicode(obj) for obj in obj_list)


@register.assignment_tag(takes_context=True)
def assignment_url_with_subdomain(context, view, subdomain=UNSET, *args, **kwargs):
    return subdomainsurls(context, view, subdomain, *args, **kwargs)


@register.simple_tag(takes_context=True)
def custom_stylesheet(context):
    output = ''
    try:
        subdomain = context['request'].subdomain
    except AttributeError:
        return output

    if not subdomain:
        return output

    if re.search(r'[^_a-zA-Z0-9\-]', subdomain):
        raise SuspiciousOperation(_('Invalid subdomain for custom CSS'))

    path = os.path.join(subdomain, 'css/custom.css')
    file_path = finders.find(path)
    if file_path is not None:
        path = os.path.join(settings.STATIC_URL, path)
        output = '<link rel="stylesheet" href="{0}" type="text/css" media="screen" />'.format(path)

    return output
