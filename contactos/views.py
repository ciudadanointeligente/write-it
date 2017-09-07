from django.views.generic.edit import UpdateView, CreateView
from .models import Contact
from .forms import ContactUpdateForm, ContactCreateForm
from django.http import HttpResponse
import simplejson as json
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from subdomains.utils import reverse
from instance.models import WriteItInstance
from popolo.models import Person
from django.http import Http404


class ContactoUpdateView(UpdateView):
    model = Contact
    http_method_names = ['post', ]
    form_class = ContactUpdateForm
    # TODO update view to have a html for get does not make any sense now but may be in the future
    template_name = "contactos/mails/bounce_notification.html"
    content_type = 'application/json'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.queryset = Contact.objects.filter(writeitinstance__owner=self.request.user)
        return super(ContactoUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        self.object.is_bounced = False
        self.object.save()
        return self.render_to_response({'contact': {'value': self.object.value}})

    def render_to_response(self, context, **response_kwargs):
        data = json.dumps(context)
        return HttpResponse(data, content_type=self.content_type)


class ContactCreateView(CreateView):
    model = Contact
    # TODO update view to have a html for get does not make any sense now but may be in the future
    template_name = "nuntium/profiles/contacts/create_new_contact_form.html"
    form_class = ContactCreateForm

    def get_success_url(self):
        return reverse('contacts-per-writeitinstance', subdomain=self.writeitinstance.slug)

    def get_form_kwargs(self):
        kwargs = super(ContactCreateView, self).get_form_kwargs()
        self.writeitinstance = WriteItInstance.objects.get(id=self.kwargs['pk'])
        person = Person.objects.get(id=self.kwargs['person_pk'])
        kwargs['writeitinstance'] = self.writeitinstance
        kwargs['person'] = person
        return kwargs


class ToggleContactEnabledView(UpdateView):
    http_method_names = ['post', ]
    model = Contact
    fields = ['enabled']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.queryset = Contact.objects.filter(writeitinstance__owner=self.request.user)
        return super(ToggleContactEnabledView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        id_ = self.request.POST['id']
        try:
            contact = self.queryset.get(id=id_)
            self.original_enabled = contact.enabled
        except Contact.DoesNotExist:
            raise Http404
        return contact

    def form_valid(self, form):
        self.object.enabled = not self.original_enabled
        self.object.save()
        data = json.dumps({
            'contact': {
                'id': self.object.id,
                'enabled': self.object.enabled
            }
            })
        return HttpResponse(data, content_type='application/json')
