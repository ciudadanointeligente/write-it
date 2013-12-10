from django.views.generic.edit import UpdateView
from .models import Contact
from .forms import ContactUpdateForm
from django.http import HttpResponse
import simplejson as json
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class ContactoUpdateView(UpdateView):
    model = Contact
    http_method_names = ['post', ]
    form_class = ContactUpdateForm
    template_name = "contactos/mails/bounce_notification.html"
    content_type = 'application/json'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.queryset = Contact.objects.filter(owner=self.request.user)
        return super(ContactoUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        self.object.is_bounced=False
        self.object.save()
        return self.render_to_response({'contact':{'value':self.object.value}})

    def render_to_response(self, context, **response_kwargs):
        data = json.dumps(context)
        return HttpResponse(data, mimetype=self.content_type)
        




