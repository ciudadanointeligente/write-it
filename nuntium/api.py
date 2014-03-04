# -*- coding: utf-8 -*-
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS, Resource
from nuntium.models import WriteItInstance, Message, Answer, \
                            OutboundMessageIdentifier, OutboundMessage, \
                            Confirmation
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization
from django.core.exceptions import ObjectDoesNotExist
from django.conf.urls import url
from tastypie import fields
from tastypie.exceptions import ImmediateHttpResponse
from tastypie import http
from popit.models import Person
from contactos.models import Contact
from tastypie.paginator import Paginator
from django.http import Http404, HttpResponseBadRequest
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

class PagePaginator(Paginator):
    def get_offset(self):
        if 'page' in self.request_data:
            return self.get_offset_from_page()
        return super(PagePaginator, self).get_offset()

    def get_offset_from_page(self):
        page = int(self.request_data.get('page'))
        offset = (page - 1) * self.get_limit()
        return offset
        

class PersonResource(ModelResource):
    class Meta:
        queryset = Person.objects.all()
        resource_name = 'person'
        authentication = ApiKeyAuthentication()

    def dehydrate(self, bundle):
        bundle.data['resource_uri'] = bundle.obj.popit_url
        return bundle

class WriteItInstanceResource(ModelResource):
    # I should add persons but the thing is that
    # it breaks some other tests and I'm running out of time
    # so now you cannot create a writeit instance with persons
    # just with a popit-instance =)
    # regards the lazy programmer
    class Meta:
        queryset = WriteItInstance.objects.all()
        resource_name = 'instance'
        authorization = Authorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/(?P<id>[-\d]+)/messages/$" %
                 self._meta.resource_name,\
                 self.wrap_view('handle_instance_messages'),
                 name="api_handle_messages"),
        ]

    def handle_instance_messages(self,request, *args, **kwargs):
        basic_bundle = self.build_bundle(request=request)
        obj = self.cached_obj_get(bundle=basic_bundle, \
                        **self.remove_api_resource_names(kwargs))
        return MessageResource().get_list(request, writeitinstance=obj)


    def dehydrate(self, bundle):
        #not completely sure that this is the right way to get the messages
        bundle.data['messages_uri'] = bundle.data['resource_uri']+'messages/'
        self.add_persons_to_bundle(bundle)
        return bundle

    def add_persons_to_bundle(self, bundle):
        bundle.data['persons'] = []
        for person in bundle.obj.persons.all():
            bundle.data['persons'].append(person.popit_url)
        return bundle

    def hydrate(self, bundle):
        bundle.obj.owner = bundle.request.user
        return bundle

    def obj_create(self, bundle):
        bundle = super(WriteItInstanceResource, self).obj_create(bundle)
        instance = bundle.obj
        if "popit-api" in bundle.data and bundle.data["popit-api"]:
            instance.load_persons_from_a_popit_api(bundle.data["popit-api"])
        return bundle

class AnswerResource(ModelResource):
    class Meta:
        queryset =  Answer.objects.all()
        resource_name = 'answer'

class MessageResource(ModelResource):
    writeitinstance = fields.ToOneField(WriteItInstanceResource, \
        'writeitinstance')
    answers = fields.ToManyField(AnswerResource, 'answers', \
        null=True, \
        full=True)
    people = fields.ToManyField(PersonResource, 'people', \
        null=True, \
        readonly=True, \
        full=True)

    class Meta:
        queryset = Message.public_objects.all().order_by('-created')
        # About the ordering
        # ordering = ['-created']
        # should work but it doesn't so I put it in the queryset
        resource_name = 'message'
        authorization = Authorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        paginator_class = PagePaginator
        filtering = {
            'writeitinstance': ALL_WITH_RELATIONS
        }

    def build_filters(self, filters=None):
        result = super(MessageResource, self).build_filters(filters)
        person = None
        if 'person' in filters:
            try:
                person = Person.objects.get(id=filters['person'])
            except:
                raise Http404("Person does not exist")
        if 'person__popit_id' in filters:
            try:
                person = Person.objects.get(popit_id=filters['person__popit_id'])
            except ObjectDoesNotExist, e:
                raise Http404("Person does not exist")
        if person:
            result['person'] = person
        return result

    def hydrate(self, bundle):
        persons = []
        instance = WriteItInstanceResource().get_via_uri(
                bundle.data["writeitinstance"]
                )
        if not instance.autoconfirm_api_messages:
            if not 'author_email' in bundle.data:
                raise ImmediateHttpResponse(response=HttpResponseBadRequest("The author has no email"))
        if 'author_email' in bundle.data:
            # Validating author_email
            try:
                validate_email(bundle.data['author_email'])
            except ValidationError, e:
                raise ImmediateHttpResponse(response=HttpResponseBadRequest(e.__str__()))

        if bundle.data['persons'] == 'all':
            for person in instance.persons.all():
                persons.append(person)
        else:
            for popit_url in bundle.data['persons']:
                try:
                    person = Person.objects.get(popit_url=popit_url)
                    persons.append(person)
                except ObjectDoesNotExist:
                    pass
        bundle.obj.persons = persons
        bundle.obj.confirmated = True
        return bundle

    def dehydrate(self, bundle):
        bundle.data['persons'] = []
        for person in bundle.obj.people:
            bundle.data['persons'].append(person.popit_url)
        return bundle

    def obj_create(self, bundle, **kwargs):
        bundle = super(MessageResource, self).obj_create(bundle, **kwargs)
        if bundle.obj.writeitinstance.autoconfirm_api_messages:
            bundle.obj.recently_confirmated()
        else:
            bundle.obj.confirmated = False
            bundle.obj.save()
            Confirmation.objects.create(message=bundle.obj)
        return bundle

class AnswerCreationResource(Resource):
    class Meta:
        resource_name = 'create_answer'
        object_class = Answer
        authentication = ApiKeyAuthentication()
        allowed_methods = ['post', ]


    def obj_create(self, bundle, **kwargs):
        identifier_key = bundle.data['key']
        identifier = OutboundMessageIdentifier.objects.get(key=bundle.data['key'])
        owner = identifier.outbound_message.message.writeitinstance.owner
        
        if owner != bundle.request.user:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())

        answer_content = bundle.data['content']
        OutboundMessageIdentifier.create_answer(identifier_key, answer_content)


class HandleBouncesResource(Resource):
    class Meta:
        resource_name = 'handle_bounce'
        object_class = Contact
        authentication = ApiKeyAuthentication()
        allowed_methods = ['post', ]


    def obj_create(self, bundle, **kwargs):
        identifier_key = bundle.data['key']
        identifier = OutboundMessageIdentifier.objects.get(key=identifier_key)
        outbound_message = OutboundMessage.objects.get(
            outboundmessageidentifier=identifier
            )
        contact = outbound_message.contact
        contact.is_bounced = True
        contact.save()
        