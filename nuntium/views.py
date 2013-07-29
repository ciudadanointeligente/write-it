# Create your views here.
from django.views.generic import TemplateView, CreateView, DetailView, RedirectView
from django.core.urlresolvers import reverse
from nuntium.models import WriteItInstance, Confirmation, OutboundMessage, Message, Moderation
from nuntium.forms import MessageCreateForm
from datetime import datetime
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.contrib import messages


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

    def get_object(self):
        subdomain = self.request.subdomain
        if not self.object:
            self.object = self.model.objects.get(slug=subdomain)
        return self.object


    def form_valid(self, form):
        messages.success(self.request, _("Thanks for submitting your message, please check your email and click on the confirmation link"))
        response = super(WriteItInstanceDetailView, self).form_valid(form)
        return response


    def get_success_url(self):
        return self.object.writeitinstance.get_absolute_url()

    def get_form_kwargs(self):
        kwargs = super(WriteItInstanceDetailView, self).get_form_kwargs()
        self.object = self.get_object()
        kwargs['writeitinstance'] = self.object        
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(WriteItInstanceDetailView, self).get_context_data(**kwargs)
        public_messages = self.get_object().message_set.filter(Q(public=True) & Q(confirmated=True))
        context['public_messages'] = public_messages
        return context

class MessageDetailView(DetailView):
    template_name='nuntium/message_detail.html'
    model=Message

    def get_queryset(self):
        #get_object_or_404(Message, slug__iexact=self.kwargs['slug'])
        qs = Message.objects.filter(slug__iexact=self.kwargs['slug'])

        is_confirmed = False
        if qs[0].confirmated:
            is_confirmed = qs[0].confirmated
        else:
            try:
                is_confirmed = qs[0].confirmation.is_confirmed
            except :
                pass


        if not is_confirmed:
            raise Http404
        return qs

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
        confirmation.message.recently_confirmated()
        return super(ConfirmView,self).get(*args, **kwargs)

class ModerationView(DetailView):
    model = Moderation
    slug_field = 'key'

class AcceptModerationView(ModerationView):
    template_name = "nuntium/moderation_accepted.html"
    

    def get(self, *args, **kwargs):
        moderation = self.get_object()
        moderation.message.set_to_ready()
        return super(AcceptModerationView, self).get(*args,**kwargs)


class RejectModerationView(ModerationView):
    template_name = "nuntium/moderation_rejected.html"

    def get(self, *args, **kwargs):        
        get = super(RejectModerationView, self).get(*args,**kwargs)
        self.get_object().message.delete()
        return get


class RootRedirectView(RedirectView):
    def get_redirect_url(self, **kwargs):

        url = reverse("home")
        return url