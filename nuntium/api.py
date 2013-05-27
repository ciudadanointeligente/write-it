
from tastypie.resources import ModelResource
from nuntium.models import WriteItInstance, Message
from tastypie.authentication import ApiKeyAuthentication
from django.conf.urls import url
from tastypie import fields

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
        return resource.get_list(request, writeitinstance_id=obj.pk)



class MessageResource(ModelResource):
    class Meta:
        queryset = Message.objects.all()
        resource_name = 'message'
        authentication = ApiKeyAuthentication()
