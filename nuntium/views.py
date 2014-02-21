from django.views.generic import TemplateView, CreateView, DetailView, RedirectView, View, ListView
from django.views.generic.edit import UpdateView
from subdomains.utils import reverse
from django.core.urlresolvers import reverse as original_reverse
from nuntium.models import WriteItInstance, Confirmation, OutboundMessage, Message, Moderation, Membership,\
                            NewAnswerNotificationTemplate
from nuntium.forms import MessageCreateForm, WriteItInstanceBasicForm, NewAnswerNotificationTemplateForm,\
                        MessageSearchForm, PerInstanceSearchForm
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.contrib import messages
from haystack.views import SearchView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from contactos.models import Contact
from contactos.forms import ContactCreateForm
from django.http import Http404
from mailit.forms import MailitTemplateForm
from popit.models import Person

class HomeTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(HomeTemplateView, self).get_context_data(**kwargs)
        all_instances = WriteItInstance.objects.all()

        context['writeitinstances'] = all_instances
        return context

class WriteItInstanceListView(ListView):
    model = WriteItInstance

class WriteItInstanceDetailView(CreateView):
    form_class = MessageCreateForm
    model = WriteItInstance
    template_name='nuntium/instance_detail.html'

    def get_object(self):
        subdomain = self.request.subdomain
        if not self.object:
            try:
                self.object = self.model.objects.get(slug=subdomain)
            except WriteItInstance.DoesNotExist, e:
                raise Http404
            
        return self.object


    def form_valid(self, form):
        response = super(WriteItInstanceDetailView, self).form_valid(form)
        moderations = Moderation.objects.filter(message=self.object)
        if moderations.count() > 0 or self.object.writeitinstance.moderation_needed_in_all_messages:
            messages.success(self.request, _("Thanks for submitting your message, please check your email and click on the confirmation link, after that your message will be waiting form moderation"))
        else:
            messages.success(self.request, _("Thanks for submitting your message, please check your email and click on the confirmation link"))
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
        public_messages = Message.objects.public(writeitinstance=self.object)
        context['public_messages'] = public_messages
        context['search_form'] = PerInstanceSearchForm(writeitinstance=self.object)
        return context

class MessageDetailView(DetailView):
    template_name='nuntium/message/message_detail.html'
    model=Message

    def get_queryset(self):
        qs = Message.objects.filter(slug__iexact=self.kwargs['slug'])
        return qs

    def get_object(self):
        the_message = super(MessageDetailView, self).get_object()
        if not the_message.public:
            raise Http404
        is_confirmed = False
        if the_message.confirmated:
            is_confirmed = the_message.confirmated
        else:
            is_confirmed = the_message.confirmation.is_confirmed

        return the_message

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
        moderation.message.moderate()
        return super(AcceptModerationView, self).get(*args,**kwargs)


class RejectModerationView(ModerationView):
    template_name = "nuntium/moderation_rejected.html"

    def get(self, *args, **kwargs):        
        get = super(RejectModerationView, self).get(*args,**kwargs)
        self.get_object().message.delete()
        return get


class RootRedirectView(RedirectView):
    def get_redirect_url(self, **kwargs):

        url = original_reverse("home")
        return url

class MessageSearchView(SearchView):
    

    def __init__(self, *args, **kwargs):
        super(MessageSearchView, self).__init__(*args, **kwargs)
        self.form_class = MessageSearchForm
        self.template = 'nuntium/search.html'

class PerInstanceSearchView(SearchView):
    def __init__(self, *args, **kwargs):
        super(PerInstanceSearchView, self).__init__(*args, **kwargs)
        self.form_class = PerInstanceSearchForm
        self.template = 'nuntium/instance_search.html'


    def build_form(self, form_kwargs=None):
        self.writeitinstance = WriteItInstance.objects.get(slug=self.request.subdomain)
        if form_kwargs is None:
            form_kwargs = {}
        form_kwargs['writeitinstance']=self.writeitinstance

        return super(PerInstanceSearchView, self).build_form(form_kwargs)


class UserAccountView(TemplateView):
    template_name = 'nuntium/profiles/your-profile.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserAccountView, self).dispatch(*args, **kwargs)

class WriteItInstanceTemplateUpdateView(DetailView):
    model = WriteItInstance
    template_name = 'nuntium/profiles/templates.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(WriteItInstanceTemplateUpdateView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        self.object = super(WriteItInstanceTemplateUpdateView, self).get_object(queryset=queryset)
        #OK I don't know if it is better to test by id
        if not self.object.owner.__eq__(self.request.user):
            raise Http404
        return self.object

    def get_context_data(self,**kwargs):
        context = super(WriteItInstanceTemplateUpdateView, self).get_context_data(**kwargs)
        context['new_answer_template_form'] = NewAnswerNotificationTemplateForm(writeitinstance=self.object, 
            instance=self.object.new_answer_notification_template)

        context['mailit_template_form'] = MailitTemplateForm(writeitinstance=self.object, \
            instance=self.object.mailit_template
            )
        return context

class WriteItInstanceUpdateView(UpdateView):
    form_class = WriteItInstanceBasicForm
    template_name_suffix = '_update_form'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.queryset = WriteItInstance.objects.filter(owner=self.request.user)
        return super(WriteItInstanceUpdateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('writeitinstance_basic_update', kwargs={'pk':self.object.pk})

    def form_valid(self, form):
        # I've been using this 
        # solution http://stackoverflow.com/questions/12224442/class-based-views-for-m2m-relationship-with-intermediate-model
        # but I think this logic can be moved to the form instead
        # and perhaps use the same form for creating and updating
        # a writeit instance
        self.object = form.save(commit=False)
        Membership.objects.filter(writeitinstance=self.object).delete()
        for person in form.cleaned_data['persons']:
            membership = Membership.objects.create(writeitinstance=self.object, person=person)

        del form.cleaned_data['persons']


        form.save_m2m()
        response = super(WriteItInstanceUpdateView, self).form_valid(form)
        
        return response


class UserSectionListView(ListView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserSectionListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = super(UserSectionListView, self).get_queryset().filter(owner=self.request.user)
        return queryset



class YourContactsView(UserSectionListView):
    model = Contact
    template_name = 'nuntium/profiles/your-contacts.html'


    def get_context_data(self,**kwargs):
        context = super(YourContactsView, self).get_context_data(**kwargs)
        context['form'] = ContactCreateForm(owner=self.request.user)
        return context

class YourInstancesView(UserSectionListView):
    model = WriteItInstance
    template_name = 'nuntium/profiles/your-instances.html'


class NewAnswerNotificationTemplateUpdateView(UpdateView):
    form_class = NewAnswerNotificationTemplateForm
    model = NewAnswerNotificationTemplate

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NewAnswerNotificationTemplateUpdateView, self).dispatch(*args, **kwargs)

    def get_object(self):
        self.writeitinstance = get_object_or_404(WriteItInstance, pk=self.kwargs['pk'])
        if not self.writeitinstance.owner.__eq__(self.request.user):
            raise Http404
        self.object = NewAnswerNotificationTemplate.objects.get(writeitinstance=self.writeitinstance)
        return self.object

    def get_form_kwargs(self):
        kwargs = super(NewAnswerNotificationTemplateUpdateView, self).get_form_kwargs()
        kwargs['writeitinstance'] = self.writeitinstance        
        return kwargs

    def get_success_url(self):
        return reverse('writeitinstance_template_update', kwargs={'pk':self.writeitinstance.pk})


class MessagesPerPersonView(ListView):
    model = Message
    template_name = "nuntium/message/per_person.html"

    def dispatch(self, *args, **kwargs):
        self.person = Person.objects.get(id=self.kwargs['pk'])
        self.subdomain = self.request.subdomain
        self.writeitinstance = WriteItInstance.objects.get(slug=self.subdomain)
        return super(MessagesPerPersonView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = Message.objects.public(
            person=self.person,
            writeitinstance=self.writeitinstance,
            )
        return qs

    def get_context_data(self,**kwargs):
        context = super(MessagesPerPersonView, self).get_context_data(**kwargs)
        context['person'] = self.person
        return context