from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from .views import UserAccountView, WriteItInstanceUpdateView, \
    YourInstancesView, WriteItInstanceAdvancedUpdateView, \
    WriteItInstanceTemplateUpdateView, NewAnswerNotificationTemplateUpdateView, \
    ConfirmationTemplateUpdateView, WriteItInstanceCreateView, \
    MessagesPerWriteItInstance, \
    MessageDetail, MessageDelete, AnswerCreateView, ModerationView, AnswerUpdateView, \
    WriteitPopitRelatingView, WriteItDeleteView, WriteItInstanceContactDetailView, \
    WriteItInstanceStatusView, WriteItInstanceApiDocsView

urlpatterns = patterns('',
    url(r'^accounts/profile/?$', UserAccountView.as_view(), name='account'),
    url(r'^accounts/your_instances/?$', YourInstancesView.as_view(), name='your-instances'),
    url(r'^writeitinstance/edit/(?P<pk>[-\d]+)/?$', WriteItInstanceUpdateView.as_view(),
        name='writeitinstance_basic_update'),
    url(r'^writeitinstance/advanced_edit/(?P<pk>[-\d]+)/?$',
        WriteItInstanceAdvancedUpdateView.as_view(),
        name='writeitinstance_advanced_update'),
    url(r'^writeitinstance/(?P<pk>[-\d]+)/messages/?$',
        MessagesPerWriteItInstance.as_view(),
        name='messages_per_writeitinstance'),
    url(r'^writeitinstance/(?P<pk>[-\d]+)/contacts/?$',
        WriteItInstanceContactDetailView.as_view(),
        name='contacts-per-writeitinstance'),
    url(r'^writeitinstance/(?P<pk>[-\d]+)/api_docs/?$',
        WriteItInstanceApiDocsView.as_view(),
        name='writeitinstance_api_docs'),
    url(r'^message/(?P<pk>[-\d]+)/answers/?$',
        MessageDetail.as_view(),
        name='message_detail'),
    url(r'^message/(?P<pk>[-\d]+)/create_answers/?$',
        AnswerCreateView.as_view(),
        name='create_answer'),
    url(r'^message/answers/update_answers/(?P<pk>[-\d]+)/?$',
        AnswerUpdateView.as_view(),
        name='update_answer'),
    url(r'^message/(?P<pk>[-\d]+)/delete/?$',
        MessageDelete.as_view(),
        name='message_delete'),

    url(r'^message/(?P<pk>[-\d]+)/moderate/?$',
        ModerationView.as_view(),
        name='moderate_message'),

    url(r'^writeitinstance/edit/(?P<pk>[-\d]+)/templates/?$',
        WriteItInstanceTemplateUpdateView.as_view(),
        name='writeitinstance_template_update'),
    url(r'^writeitinstance/edit/(?P<pk>[-\d]+)/templates/new_answer_notification/?$',
        NewAnswerNotificationTemplateUpdateView.as_view(),
        name='edit_new_answer_notification_template'),
    url(r'^writeitinstance/edit/(?P<pk>[-\d]+)/templates/confirmation_template/?$',
        ConfirmationTemplateUpdateView.as_view(),
        name='edit_confirmation_template'),
    url(r'^writeitinstance/create/?$',
        WriteItInstanceCreateView.as_view(),
        name='create_writeit_instance'),
    url(r'^docs/?$',
        TemplateView.as_view(template_name="nuntium/profiles/docs.html"),
        name='user_section_documentation'),
    url(r'^writeitinstance/edit/(?P<pk>[-\d]+)/relate-with-popit/?$',
        WriteitPopitRelatingView.as_view(),
        name='relate-writeit-popit'),
    url(r'^writeitinstance/delete/(?P<pk>[-\d]+)/?$',
        WriteItDeleteView.as_view(template_name="nuntium/profiles/writeitinstance_check_delete.html"),
        name='delete_an_instance'),
    url(r'^writeitinstance/pulling_status/(?P<pk>[-\d]+)/?$',
        WriteItInstanceStatusView.as_view(),
        name='pulling_status'),
)
