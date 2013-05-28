# -*- coding: utf-8 -*-
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from nuntium.models import WriteItInstance, Message, Answer
from tastypie.authentication import ApiKeyAuthentication
from django.conf.urls import url
from tastypie import fields
from django.http import HttpRequest

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



class MessageResource(ModelResource):
    writeitinstance = fields.ToOneField(WriteItInstanceResource, 'writeitinstance')
    class Meta:
        queryset = Message.objects.all()
        resource_name = 'message'
        authentication = ApiKeyAuthentication()
        filtering = {
            'writeitinstance': ALL_WITH_RELATIONS
        }

class AnswerResource(ModelResource):
    class Meta:
        queryset =  Answer.objects.all()
