from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from mailit.views import MailitTemplateUpdateView
from nuntium.views import (
    AcceptModerationView,
    ConfirmView,
    HomeTemplateView,
    WriteMessageView,
    MessageSearchView,
    RejectModerationView,
    WriteItInstanceDetailView,
    WriteItInstanceListView,
    )
from nuntium.user_section.views import (
    AcceptMessageView,
    AnswerCreateView,
    AnswerUpdateView,
    ConfirmationTemplateUpdateView,
    MessageDelete,
    MessageDetail,
    MessagesPerWriteItInstance,
    NewAnswerNotificationTemplateUpdateView,
    WriteItDeleteView,
    WriteItInstanceAdvancedUpdateView,
    WriteItInstanceApiDocsView,
    WriteItInstanceContactDetailView,
    WriteItInstanceStatusView,
    WriteItInstanceTemplateUpdateView,
    WriteItInstanceUpdateView,
    WriteitPopitRelatingView,
)
from nuntium.user_section.stats import StatsView

urlpatterns = patterns('',
    # Examples:
    url(r'^$', HomeTemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^instances/?$', WriteItInstanceListView.as_view(template_name='nuntium/template_list.html'), name='instance_list'),

    url(r'^search/?$', MessageSearchView(), name='search_messages'),

    url(r'^confirm_message/(?P<slug>[-\w]+)/?$', ConfirmView.as_view(), name='confirm'),

    url(r'^moderation_accept/(?P<slug>[-\w]+)/?$', AcceptModerationView.as_view(), name='moderation_accept'),
    url(r'^moderation_reject/(?P<slug>[-\w]+)/?$', RejectModerationView.as_view(), name='moderation_rejected'),

)
