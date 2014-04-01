# -*- coding: utf-8 -*-
from tastypie.resources import ModelResource
from popit.models import Person
from tastypie.authentication import ApiKeyAuthentication

class PersonResource(ModelResource):
    class Meta:
        queryset = Person.objects.all()
        resource_name = 'person'
        authentication = ApiKeyAuthentication()

    def dehydrate(self, bundle):
        bundle.data['resource_uri'] = bundle.obj.popit_url
        return bundle