from django.conf.urls import patterns, include, url
from nuntium.views import ConfirmView, AcceptModerationView, RejectModerationView, RootRedirectView
from django.conf.urls.i18n import i18n_patterns
from tastypie.api import Api
from nuntium.api import WriteItInstanceResource, MessageResource, AnswerCreationResource, HandleBouncesResource, PersonResource
from django.views.generic.base import TemplateView, RedirectView
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(WriteItInstanceResource())
v1_api.register(MessageResource())
v1_api.register(AnswerCreationResource())
v1_api.register(HandleBouncesResource())
v1_api.register(PersonResource())

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^/?$', RootRedirectView.as_view() ),
    url(r'^confirm_message/(?P<slug>[-\w]+)/?$', ConfirmView.as_view(), name = 'confirm'),
    url(r'^moderation_accept/(?P<slug>[-\w]+)/?$', AcceptModerationView.as_view(), name = 'moderation_accept'),
    url(r'^moderation_reject/(?P<slug>[-\w]+)/?$', RejectModerationView.as_view(), name = 'moderation_rejected'),
    (r'^api/', include(v1_api.urls)),
    url(r'^contactos/', include('contactos.urls')),


)

urlpatterns += i18n_patterns('',
    
    url(r'^', include('nuntium.urls')),
    
    (r'accounts/', include('django.contrib.auth.urls')),
)