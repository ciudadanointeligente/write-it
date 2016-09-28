from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.edit import FormView

from subdomains.utils import reverse

from .forms import ContactInstanceOwnerForm
from .models import WriteItInstance


def send_email_to_instance_owner(subject, writeitiinstance, from_email, message):
    send_mail(
        'Suggestion for missing email addresses',
        message,
        from_email,
        [writeitiinstance.owner.email])


class InstanceMixin(object):

    def dispatch(self, *args, **kwargs):
        self.writeitinstance = get_object_or_404(
            WriteItInstance, slug=self.request.subdomain)
        return super(InstanceMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(InstanceMixin, self).get_context_data(**kwargs)
        context['writeitinstance'] = self.writeitinstance
        return context


class ContactInstanceOwnerView(InstanceMixin, FormView):
    form_class = ContactInstanceOwnerForm
    template_name = 'instance/contact_instance_owner.html'

    def get_success_url(self):
        return reverse('instance_detail', subdomain=self.writeitinstance.slug)

    def form_valid(self, form):
        send_email_to_instance_owner(
            'Suggestion for missing email addresses',
            self.writeitinstance,
            form.cleaned_data['from_email'],
            form.cleaned_data['message_content']
        )
        return HttpResponseRedirect(self.get_success_url())
