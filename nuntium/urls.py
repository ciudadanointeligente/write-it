from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from nuntium.views import HomeTemplateView, MessageSearchView, UserAccountView, \
                            WriteItInstanceDetailView, WriteItInstanceUpdateView, \
                            YourContactsView, YourInstancesView, WriteItInstanceTemplateUpdateView,\
                            NewAnswerNotificationTemplateUpdateView, WriteItInstanceListView


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', HomeTemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^instances/?$', WriteItInstanceListView.as_view(template_name='nuntium/template_list.html'), name='instance_list'),

    url(r'^search/?$', MessageSearchView(), name='search_messages'),
    url(r'^accounts/profile/?$', UserAccountView.as_view(), name='account'),
    url(r'^accounts/your_contacts/?$', YourContactsView.as_view(), name='your-contacts'),
    url(r'^accounts/your_instances/?$', YourInstancesView.as_view(), name='your-instances'),
    url(r'^writeitinstance/edit/(?P<pk>[-\d]+)/?$', WriteItInstanceUpdateView.as_view(), name = 'writeitinstance_basic_update'),
    url(r'^writeitinstance/edit/(?P<pk>[-\d]+)/templates/?$', \
        WriteItInstanceTemplateUpdateView.as_view(), \
        name = 'writeitinstance_template_update'),
    url(r'^writeitinstance/edit/(?P<pk>[-\d]+)/templates/new_answer_notification/?$', 
        NewAnswerNotificationTemplateUpdateView.as_view(), 
        name = 'edit_new_answer_notification_template'),
)