# -*- coding: utf-8 -*-
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from nuntium.models import WriteItInstance, Message, Answer
from tastypie.authentication import ApiKeyAuthentication, Authentication
from tastypie.authorization import Authorization
from django.conf.urls import url
from tastypie import fields
from django.http import HttpRequest
from popit.models import Person

class WriteItInstanceResource(ModelResource):
    class Meta:
        queryset = WriteItInstance.objects.all()
        resource_name = 'instance'
        authentication = ApiKeyAuthentication()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<id>[-\d]+)/messages/$" % self._meta.resource_name, self.wrap_view('handle_instance_messages'), name="api_handle_messages"),
        ]

    def handle_instance_messages(self,request, *args, **kwargs):
        basic_bundle = self.build_bundle(request=request)
        obj = self.cached_obj_get(bundle=basic_bundle, **self.remove_api_resource_names(kwargs))
        resource = MessageResource()
        return resource.get_list(request, writeitinstance=obj)


    def dehydrate(self, bundle):
        #not completely sure that this is the right way to get the messages
        bundle.data['messages'] = bundle.data['resource_uri']+'messages/'
        return bundle


class AnswerResource(ModelResource):
    class Meta:
        queryset =  Answer.objects.all()
        resource_name = 'answer'

class MessageResource(ModelResource):
    writeitinstance = fields.ToOneField(WriteItInstanceResource, 'writeitinstance')
    answers = fields.ToManyField(AnswerResource, 'answers', null=True, full=True)

    class Meta:
        queryset = Message.objects.all()
        resource_name = 'message'
        authorization = Authorization()
        authentication = ApiKeyAuthentication()
        filtering = {
            'writeitinstance': ALL_WITH_RELATIONS
        }

    def hydrate(self, bundle):
        persons = []
        for popit_url in bundle.data['persons']:
            persons.append(Person.objects.get(popit_url=popit_url))
        bundle.obj.persons = persons
        bundle.obj.confirmated = True
        return bundle

    def obj_create(self, bundle, **kwargs):
        bundle = super(MessageResource, self).obj_create(bundle, **kwargs)
        bundle.obj.recently_confirmated()
        return bundle


