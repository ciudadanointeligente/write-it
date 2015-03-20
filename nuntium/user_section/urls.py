from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from contactos.views import ToggleContactEnabledView
from nuntium.user_section.stats import StatsView
from .views import UserAccountView, \
    YourInstancesView, \
    WriteItInstanceTemplateUpdateView, NewAnswerNotificationTemplateUpdateView, \
    ConfirmationTemplateUpdateView, WriteItInstanceCreateView, \
    MessageDetail, MessageDelete, AnswerCreateView, AnswerUpdateView, \
    WriteItDeleteView, WriteItInstanceContactDetailView, \
    WriteItInstanceStatusView

urlpatterns = patterns('',
    url(r'^accounts/profile/?$', UserAccountView.as_view(), name='account'),
    url(r'^accounts/your_instances/?$', YourInstancesView.as_view(), name='your-instances'),

    url(r'^contactos/contacto/toggle-enabled/?$',
        ToggleContactEnabledView.as_view(),
        name='toggle-enabled'),

    url(r'^writeitinstance/create/?$',
        WriteItInstanceCreateView.as_view(),
        name='create_writeit_instance'),
    url(r'^writeitinstance/delete/(?P<pk>[-\d]+)/?$',
        WriteItDeleteView.as_view(template_name="nuntium/profiles/writeitinstance_check_delete.html"),
        name='delete_an_instance'),
    url(r'^writeitinstance/pulling_status/(?P<pk>[-\d]+)/?$',
        WriteItInstanceStatusView.as_view(),
        name='pulling_status'),
    url(r'^writeitinstance/stats/(?P<pk>[-\d]+)/?$',
        StatsView.as_view(),
        name='stats'),

    url(r'^docs/?$',
        TemplateView.as_view(template_name="nuntium/profiles/docs.html"),
        name='user_section_documentation'),

)
