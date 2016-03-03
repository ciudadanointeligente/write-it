from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from .views import (
    UserAccountView,
    YourInstancesView,
    WriteItInstanceCreateView,
    UserRegisterView,
    )

urlpatterns = patterns('',
    url(r'^accounts/profile/?$', UserAccountView.as_view(), name='account'),
    url(r'^accounts/your_instances/?$', YourInstancesView.as_view(), name='your-instances'),
    url(r'^accounts/register/?$', UserRegisterView.as_view(), name='register'),

    url(r'^writeitinstance/create/?$',
        WriteItInstanceCreateView.as_view(),
        name='create_writeit_instance'),

    url(r'^docs/?$',
        TemplateView.as_view(template_name="nuntium/profiles/docs.html"),
        name='user_section_documentation'),
)
