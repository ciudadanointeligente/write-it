from django.db import models
from popit.models import Person
from django.utils.translation import ugettext as _

class ContactType(models.Model):
    """This class contain all contact types"""
    name = models.CharField(max_length=255)
    label_name = models.CharField(max_length=255)

    def __unicode__(self):
    	return self.label_name

class Contact(models.Model):
    """docstring for Contact"""
    contact_type = models.ForeignKey('ContactType')
    person = models.ForeignKey(Person)
    value = models.CharField(max_length=512)

    def __unicode__(self):
    	return _('%(contact)s (%(type)s)') % {
	            'contact' : self.value,
	            'type' : self.contact_type.label_name
	        }