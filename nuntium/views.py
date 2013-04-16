# Create your views here.
from django.views.generic import TemplateView, CreateView
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
    