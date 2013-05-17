# Create your views here.
from django.views.generic import TemplateView, CreateView, DetailView
from django.core.urlresolvers import reverse
from nuntium.models import WriteItInstance, Confirmation, OutboundMessage, Message
from nuntium.forms import MessageCreateForm
from datetime import datetime
from django.http import Http404



class HomeTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(HomeTemplateView, self).get_context_data(**kwargs)
        all_instances = WriteItInstance.objects.all()

        context['writeitinstances'] = all_instances
        return context

class WriteItInstanceDetailView(CreateView):
    form_class = MessageCreateForm
    model = WriteItInstance
    template_name='nuntium/instance_detail.html'

    def get_success_url(self):
        return reverse('instance_detail', kwargs={
            'slug':self.object.writeitinstance.slug
            })

    def get_form_kwargs(self):
        kwargs = super(WriteItInstanceDetailView, self).get_form_kwargs()
        self.object = self.get_object()
        kwargs['writeitinstance'] = self.object
     
        
        return kwargs
    def get_context_data(self, **kwargs):
        context = super(WriteItInstanceDetailView, self).get_context_data(**kwargs)
        public_messages = self.object.message_set.filter(public=True).exclude(confirmation__confirmated_at=None)
        context['public_messages'] = public_messages
        return context

class MessageDetailView(DetailView):
    template_name='nuntium/message_detail.html'
    model=Message

class ConfirmView(DetailView):
    template_name='nuntium/confirm.html'
    model = Confirmation
    slug_field = 'key'

    def dispatch(self, *args, **kwargs):
        confirmation = super(ConfirmView, self).get_object()
        if confirmation.confirmated_at is not None:
            raise Http404
        return super(ConfirmView,self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        confirmation = super(ConfirmView, self).get_object(queryset)

        return confirmation
    

    def get_context_data(self, **kwargs):
        context = super(ConfirmView, self).get_context_data(**kwargs)
        return context


    def get(self, *args, **kwargs):
        confirmation = self.get_object()
        confirmation.confirmated_at = datetime.now()
        confirmation.save()
        outbound_messages = OutboundMessage.objects.filter(message=confirmation.message)
        for outbound_message in outbound_messages:
            outbound_message.status="ready"
            outbound_message.save()
        return super(ConfirmView,self).get(*args, **kwargs)