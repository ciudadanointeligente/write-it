# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from urlparse import urlsplit, urlunsplit

from django.db import migrations
from django.contrib.contenttypes.management import update_contenttypes


def is_proxy_url(url):
    return url == 'everypolitician-writeinpublic.herokuapp.com'


def update_source_url(original_url):
    split_url = urlsplit(original_url)
    has_popit_in_domain = 'popit' in split_url.netloc.split('.')
    is_possible_api_url = re.match(r'/?$|^/api', split_url.path)
    if is_proxy_url(split_url.netloc):
        # If this is one of the faked PopIt instances for
        # EveryPolitician, change that to the EveryPolitican JSON.
        country, house = split_url.path.lstrip('/').split('/')[:2]
        url = ('https://raw.githubusercontent.com'
               '/everypolitician/everypolitician-data/master/data/'
               '{country}/{house}/ep-popolo-v1.0.json').format(
                   country=country, house=house)
    elif has_popit_in_domain and is_possible_api_url:
        # If looks like a PopIt instance, then replace that with a
        # link to the PopIt instance's export.json:
        split_as_list = list(split_url)
        split_as_list[2] = '/api/v0.1/export.json'
        split_as_list[3] = ''
        split_as_list[4] = ''
        url = urlunsplit(split_as_list)
    else:
        url = original_url
    return url


def forwards(apps, schema_editor):
    # Make sure the content types for django-popolo exist, with a
    # hacky workaround from: http://stackoverflow.com/a/35353170/223092
    popolo_app = apps.app_configs['popolo']
    popolo_app.models_module = popolo_app.models_module or True
    update_contenttypes(popolo_app, verbosity=1, interactive=False)
    ContentType = apps.get_model('contenttypes', 'ContentType')
    person_content_type = ContentType.objects.get(
        app_label='popolo', model='person')
    # Create a PopoloSource for each old APIInstance
    ApiInstance = apps.get_model('popit', 'ApiInstance')
    PopoloSource = apps.get_model('popolo_sources', 'PopoloSource')
    LinkToPopoloSource = apps.get_model('popolo_sources', 'LinkToPopoloSource')
    ai_to_ps = {}
    for ai in ApiInstance.objects.all():
        url = update_source_url(ai.url)
        ps = PopoloSource.objects.create(url=url)
        ai_to_ps[ai] = ps
    # Now create a django-popolo Person for each old django-popit
    # Person:
    PopItPerson = apps.get_model('popit', 'Person')
    PopoloPerson = apps.get_model('popolo', 'Person')
    Identifier = apps.get_model('popolo', 'Identifier')
    p_old_to_p_new = {}
    for popit_person in PopItPerson.objects.all():
        # The popit_ids from
        # everypolitician-writeinpublic.herokuapp.com sources have
        # 'person/' prepended, which they won't have when we switch to
        # using the upstream EveryPolitician Popolo JSON. So if it's
        # from such a source, remove that prefix.
        new_popolo_person_id = popit_person.popit_id
        if is_proxy_url(urlsplit(popit_person.popit_url).netloc):
            prefix = 'person/'
            if new_popolo_person_id.startswith(prefix):
                new_popolo_person_id = new_popolo_person_id[len(prefix):]
        # Create the new django-popolo Person object:
        new_person = PopoloPerson.objects.create(
            name=popit_person.name,
            summary=popit_person.summary,
            image=popit_person.image,
        )
        p_old_to_p_new[popit_person] = new_person
        # The popit_id Identifier is to preserve the old popit_id that
        # was on a popit-django Person. This will still be returned by
        # the API for people that have it, and will be looked up when
        # used in some URLs to avoid breaking old links. There is one
        # PopIt instance referred to in the database which has NULL
        # popit_id values, which would break the non-NULL constraint
        # on `identifier`, so only create this if it popit_id is
        # non-NULL. (Some other identifier creation, below, needs to
        # be skipped in those cases too.)
        if popit_person.popit_id:
            Identifier.objects.create(
                scheme='popit_id',
                identifier=popit_person.popit_id,
                object_id=new_person.id,
                content_type_id=person_content_type.id,
            )
        # The popit_url Identifier is to preserver the old popit_url
        # that was on a popit-django Person. This should still be used
        # as the canonical identifier for people in the API if they
        # have it, but for newer people popolo_uri will be used.
        Identifier.objects.create(
            scheme='popit_url',
            identifier=popit_person.popit_url,
            object_id=new_person.id,
            content_type_id=person_content_type.id,
        )
        # The popolo:person Identifier represents the 'id' of the
        # Person in the Popolo JSON source; it's required (among other
        # things) so that when updating from the Popolo JSON source,
        # we can tell whether a person already exists in the database
        # or not. (When fetching new people, they will have it added
        # as well.)
        if new_popolo_person_id:
            Identifier.objects.create(
                scheme='popolo:person',
                identifier=new_popolo_person_id,
                object_id=new_person.id,
                content_type_id=person_content_type.id,
            )
        # The popit_django_person_id Identifier preserved the old ID
        # of the popit-django Person object; this shouldn't be needed
        # anywhere, but it would be foolish not to preserve it in case
        # it's helpful for debugging, etc.
        Identifier.objects.create(
            scheme='popit_django_person_id',
            identifier=popit_person.id,
            object_id=new_person.id,
            content_type_id=person_content_type.id,
        )
        # This is the new canonical URI for the source of information
        # about a person, which is used in API responses where there
        # is no legacy popit_url.
        if popit_person.popit_id:
            Identifier.objects.create(
                scheme='popolo_uri',
                identifier=(ps.url + '#person-' + popit_person.popit_id),
                object_id=new_person.id,
                content_type_id=person_content_type.id,
            )
        # Set the right PopoloSource for the person:
        ps = ai_to_ps[popit_person.api_instance]
        LinkToPopoloSource.objects.create(
            popolo_source=ps,
            deleted_from_source=False,
            object_id=new_person.id,
            content_type_id=person_content_type.id,
        )
    # Update the parallel popolo_person attribute on Contact
    Contact = apps.get_model('contactos', 'Contact')
    for c in Contact.objects.all():
        c.popolo_person = p_old_to_p_new[c.person]
        c.save()
    # Create the parallel InstanceMembership relation:
    Membership = apps.get_model('instance', 'Membership')
    InstanceMembership = apps.get_model('instance', 'InstanceMembership')
    for m in Membership.objects.all():
        popolo_person = p_old_to_p_new[m.person]
        InstanceMembership.objects.create(
            person=popolo_person,
            writeitinstance=m.writeitinstance,
        )
    # Update the parallel popolo_source field on
    # WriteitInstancePopitInstanceRecord.
    WriteitInstancePopitInstanceRecord = apps.get_model(
        'instance', 'WriteitInstancePopitInstanceRecord')
    for wiipir in WriteitInstancePopitInstanceRecord.objects.all():
        wiipir.popolo_source = ai_to_ps[wiipir.popitapiinstance]
        wiipir.save()
    # Update the parallel popolo_person attribute on Answer:
    Answer = apps.get_model('nuntium', 'Answer')
    for a in Answer.objects.all():
        a.popolo_person = p_old_to_p_new[a.person]
        a.save()
    # Update the parallel popolo_person field on NoContactOM:
    NoContactOM = apps.get_model('nuntium', 'NoContactOM')
    for ncom in NoContactOM.objects.all():
        ncom.popolo_person = p_old_to_p_new[ncom.person]
        ncom.save()

def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('popit', '0001_initial'),
        ('popolo_sources', '0001_initial'),
        ('instance', '0003_add_parallel_popolo_data'),
        ('popolo', '0002_update_models_from_upstream'),
        ('contactos', '0002_contact_popolo_person'),
        ('nuntium', '0003_add_parallel_popolo_data'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards)
    ]
