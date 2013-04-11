from django.db import models
from popit.models import Person

class ContactType(models.Model):
    """This class contain all contact types"""
    name = models.CharField(max_length=255)
    label_name = models.CharField(max_length=255)

class Contact(models.Model):
    """docstring for Contact"""
    contact_type = models.ForeignKey('ContactType')
    person = models.ForeignKey(Person)
    value = models.CharField(max_length=512)