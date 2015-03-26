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

managepatterns = patterns('',
    url(r'^$', WriteItInstanceUpdateView.as_view(), name='writeitinstance_basic_update'),
    url(r'^settings/$', WriteItInstanceAdvancedUpdateView.as_view(), name='writeitinstance_advanced_update'),
    url(r'^settings/api/$', WriteItInstanceApiDocsView.as_view(), name='writeitinstance_api_docs'),
    url(r'^settings/sources/$', WriteitPopitRelatingView.as_view(), name='relate-writeit-popit'),
    url(r'^settings/templates/$', WriteItInstanceTemplateUpdateView.as_view(), name='writeitinstance_template_update'),
    url(r'^settings/templates/new_answer_notification/$', NewAnswerNotificationTemplateUpdateView.as_view(), name='edit_new_answer_notification_template'),
    url(r'^settings/templates/confirmation_template/$', ConfirmationTemplateUpdateView.as_view(), name='edit_confirmation_template'),
    url(r'^settings/templates/mailit_template/$', MailitTemplateUpdateView.as_view(), name='mailit-template-update'),
    url(r'^recipients/$', WriteItInstanceContactDetailView.as_view(), name='contacts-per-writeitinstance'),
    url(r'^messages/$', MessagesPerWriteItInstance.as_view(), name='messages_per_writeitinstance'),
    url(r'^messages/(?P<pk>[-\d]+)/answers/$', MessageDetail.as_view(), name='message_detail_private'),
    url(r'^messages/(?P<pk>[-\d]+)/answers/create/$', AnswerCreateView.as_view(), name='create_answer'),
    url(r'^messages/(?P<message_pk>[-\d]+)/answers/(?P<pk>[-\d]+)/update/$', AnswerUpdateView.as_view(), name='update_answer'),
    url(r'^messages/(?P<pk>[-\d]+)/delete/$', MessageDelete.as_view(), name='message_delete'),
    url(r'^messages/(?P<pk>[-\d]+)/accept/$', AcceptMessageView.as_view(), name='accept_message'),
    url(r'^stats/$', StatsView.as_view(), name='stats'),
    url(r'^pulling_status/$', WriteItInstanceStatusView.as_view(), name='pulling_status'),
    url(r'^delete/$',
        WriteItDeleteView.as_view(template_name="nuntium/profiles/writeitinstance_check_delete.html"),
        name='delete_an_instance'),
)

write_message_wizard = WriteMessageView.as_view(url_name='write_message_step')

# New front-end message writing process
frontendpatterns = patterns('',
    url(r'^$', WriteItInstanceDetailView.as_view(), name='instance_detail'),
    url(r'^write/sign/$', TemplateView.as_view(template_name='write/sign.html'), name='write_message_sign'),
    url(r'^write/(?P<step>.+)/$', write_message_wizard, name='write_message_step'),
    url(r'^write/$', write_message_wizard, name='write_message'),
    # url(r'^write/draft/$', TemplateView.as_view(template_name='write/draft.html'), name='write_draft'),
    # url(r'^write/preview/$', TemplateView.as_view(template_name='write/preview.html'), name='write_preview'),
    # url(r'^write/sign/(?P<token>[-\w]+)/$', SignTokenView.as_view(), name='write_sign_token'),
    url(r'^thread/(?P<pk>[-\d]+)/$', TemplateView.as_view(template_name='thread/read.html'), name='thread_read'),
    url(r'^from/(?P<pk>[-\d]+)/$', TemplateView.as_view(template_name='thread/from.html'), name='thread_from'),
    url(r'^to/(?P<pk>[-\d]+)/$', TemplateView.as_view(template_name='thread/to.html'), name='thread_to'),
)
