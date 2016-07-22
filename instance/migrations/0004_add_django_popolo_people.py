# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def forwards(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    # If you're migrating from scratch in one go, the content types
    # won't exist, but it doesn't actually matter because there won't
    # be any people to add identifiers for either. So just get the
    # content type if it's possible to do so:
    person_content_type = None
    try:
        person_content_type = ContentType.objects.get(
            app_label='popolo', model='person')
    except ContentType.DoesNotExist:
        pass
    # Create a PopoloSource for each old APIInstance
    ApiInstance = apps.get_model('popit', 'ApiInstance')
    PopoloSource = apps.get_model('instance', 'PopoloSource')
    ai_to_ps = {}
    for ai in ApiInstance.objects.all():
        ps = PopoloSource.objects.create(url=ai.url)
        ai_to_ps[ai] = ps
    # Now create a django-popolo Person for each old django-popit
    # Person:
    PopItPerson = apps.get_model('popit', 'Person')
    PopoloPerson = apps.get_model('popolo', 'Person')
    Identifier = apps.get_model('popolo', 'Identifier')
    p_old_to_p_new = {}
    for popit_person in PopItPerson.objects.all():
        new_person = PopoloPerson.objects.create(
            name=popit_person.name,
            summary=popit_person.summary,
            image=popit_person.image,
        )
        p_old_to_p_new[popit_person] = new_person
        # Save the existing identifiers, and add the new canonical
        # popolo_source_id
        Identifier.objects.create(
            scheme='popit_id',
            identifier=popit_person.popit_id,
            object_id=new_person.id,
            content_type_id=person_content_type.id,
        )
        Identifier.objects.create(
            scheme='popit_url',
            identifier=popit_person.popit_url,
            object_id=new_person.id,
            content_type_id=person_content_type.id,
        )
        Identifier.objects.create(
            scheme='popolo_source_id',
            identifier=popit_person.popit_id,
            object_id=new_person.id,
            content_type_id=person_content_type.id,
        )
        # Set the right PopoloSource for the person:
        ps = ai_to_ps[popit_person.api_instance]
        new_person.popolosource_set.add(ps)
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
        ('instance', '0003_add_parallel_popolo_data'),
        ('popolo', '0002_update_models_from_upstream'),
        ('contactos', '0002_contact_popolo_person'),
        ('nuntium', '0002_add_parallel_popolo_data'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards)
    ]