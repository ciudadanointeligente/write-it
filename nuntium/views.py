# Create your views here.
from django.views.generic import TemplateView, CreateView, DetailView
from django.core.urlresolvers import reverse
from nuntium.models import Instance
from nuntium.forms import MessageCreateForm



class HomeTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(HomeTemplateView, self).get_context_data(**kwargs)
        all_instances = Instance.objects.all()

        context['instances'] = all_instances
        return context

class InstanceDetailView(CreateView):
    form_class = MessageCreateForm
    model = Instance
    template_name='nuntium/instance_detail.html'
    success_url = '#'

    def get_form_kwargs(self):
        kwargs = super(InstanceDetailView, self).get_form_kwargs()
        self.object = self.get_object()
        kwargs['instance'] = self.object
        
        return kwargs