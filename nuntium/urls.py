from django.conf.urls import patterns, url

from nuntium.views import (
    AcceptModerationView,
    ConfirmView,
    HelpView,
    HomeTemplateView,
    MessageSearchView,
    RejectModerationView,
    WriteItInstanceListView,
    )


urlpatterns = patterns('',
    # Examples:
    url(r'^$', HomeTemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^instances/?$', WriteItInstanceListView.as_view(template_name='nuntium/template_list.html'), name='instance_list'),

    url(r'^search/?$', MessageSearchView(), name='search_messages'),

    url(r'^moderation_accept/(?P<slug>[-\w]+)/?$', AcceptModerationView.as_view(), name='moderation_accept'),
    url(r'^moderation_reject/(?P<slug>[-\w]+)/?$', RejectModerationView.as_view(), name='moderation_rejected'),

    url(r'^help/(?P<section_name>\w+)/?$', HelpView.as_view(), name='help_section'),
    url(r'^help/?$', HelpView.as_view()),
)
