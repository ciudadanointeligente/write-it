from django.views.generic import TemplateView, CreateView, DetailView, RedirectView, View, ListView
from django.views.generic.edit import UpdateView
from subdomains.utils import reverse
from django.core.urlresolvers import reverse as original_reverse
from nuntium.models import WriteItInstance, Confirmation, OutboundMessage, Message, Moderation, Membership,\
                            NewAnswerNotificationTemplate, ConfirmationTemplate
                        
from .forms import WriteItInstanceBasicForm, WriteItInstanceAdvancedUpdateForm, \
                    NewAnswerNotificationTemplateForm, ConfirmationTemplateForm
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
        context['confirmation_template_form'] = ConfirmationTemplateForm(writeitinstance=self.object, \
            instance=self.object.confirmationtemplate
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

class WriteItInstanceAdvancedUpdateView(UpdateView):
    form_class = WriteItInstanceAdvancedUpdateForm
    template_name_suffix = '_advanced_update_form'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.queryset = WriteItInstance.objects.filter(owner=self.request.user)
        return super(WriteItInstanceAdvancedUpdateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('writeitinstance_advanced_update', kwargs={'pk':self.object.pk})

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


class UpdateTemplateWithWriteitMixin(UpdateView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateTemplateWithWriteitMixin, self).dispatch(*args, **kwargs)

    def get_object(self):
        self.writeitinstance = get_object_or_404(WriteItInstance, pk=self.kwargs['pk'])
        if not self.writeitinstance.owner.__eq__(self.request.user):
            raise Http404

        self.object = self.model.objects.get(writeitinstance=self.writeitinstance)
        return self.object

    def get_form_kwargs(self):
        kwargs = super(UpdateTemplateWithWriteitMixin, self).get_form_kwargs()
        kwargs['writeitinstance'] = self.writeitinstance
        return kwargs

    def get_success_url(self):
        return reverse('writeitinstance_template_update', kwargs={'pk':self.writeitinstance.pk})

class NewAnswerNotificationTemplateUpdateView(UpdateTemplateWithWriteitMixin):
    form_class = NewAnswerNotificationTemplateForm
    model = NewAnswerNotificationTemplate

class ConfirmationTemplateUpdateView(UpdateTemplateWithWriteitMixin):
    form_class = ConfirmationTemplateForm
    model = ConfirmationTemplate