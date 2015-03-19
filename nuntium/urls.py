from django.conf.urls import patterns, url

from mailit.views import MailitTemplateUpdateView
from nuntium.views import ConfirmView, AcceptModerationView, RejectModerationView, \
    HomeTemplateView, MessageSearchView, WriteItInstanceListView
from nuntium.user_section.views import (
    WriteItInstanceUpdateView,
    WriteItInstanceAdvancedUpdateView,
    WriteItInstanceApiDocsView,
    WriteitPopitRelatingView,
    WriteItInstanceTemplateUpdateView,
    NewAnswerNotificationTemplateUpdateView,
    ConfirmationTemplateUpdateView,
)


urlpatterns = patterns('',
    # Examples:
    url(r'^$', HomeTemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^instances/?$', WriteItInstanceListView.as_view(template_name='nuntium/template_list.html'), name='instance_list'),

    url(r'^search/?$', MessageSearchView(), name='search_messages'),

    url(r'^confirm_message/(?P<slug>[-\w]+)/?$', ConfirmView.as_view(), name='confirm'),

    url(r'^moderation_accept/(?P<slug>[-\w]+)/?$', AcceptModerationView.as_view(), name='moderation_accept'),
    url(r'^moderation_reject/(?P<slug>[-\w]+)/?$', RejectModerationView.as_view(), name='moderation_rejected'),

)

managepatterns = patterns('',
    url(r'^$', WriteItInstanceUpdateView.as_view(), name='writeitinstance_basic_update'),
    url(r'^settings/?$', WriteItInstanceAdvancedUpdateView.as_view(), name='writeitinstance_advanced_update'),
    url(r'^settings/api/?$', WriteItInstanceApiDocsView.as_view(), name='writeitinstance_api_docs'),
    url(r'^settings/sources/?$', WriteitPopitRelatingView.as_view(), name='relate-writeit-popit'),
    url(r'^settings/templates/?$', WriteItInstanceTemplateUpdateView.as_view(), name='writeitinstance_template_update'),
    url(r'^settings/templates/new_answer_notification?$', NewAnswerNotificationTemplateUpdateView.as_view(), name='edit_new_answer_notification_template'),
    url(r'^settings/templates/confirmation_template?$', ConfirmationTemplateUpdateView.as_view(), name='edit_confirmation_template'),
    url(r'^settings/templates/mailit_template?$', MailitTemplateUpdateView.as_view(), name='mailit-template-update'),
)
