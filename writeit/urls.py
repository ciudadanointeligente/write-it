from django.conf.urls import patterns, include, url
from nuntium.views import ConfirmView, AcceptModerationView, RejectModerationView
from django.conf.urls.i18n import i18n_patterns
from tastypie.api import Api
from nuntium.api import WriteItInstanceResource, MessageResource, AnswerCreationResource, HandleBouncesResource
from django.views.generic.base import TemplateView
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(WriteItInstanceResource())
v1_api.register(MessageResource())
v1_api.register(AnswerCreationResource())
v1_api.register(HandleBouncesResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'writeit.views.home', name='home'),
    # url(r'^writeit/', include('writeit.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^confirm_message/(?P<slug>[-\w]+)/?$', ConfirmView.as_view(), name = 'confirm'),
    url(r'^moderation_accept/(?P<slug>[-\w]+)/?$', AcceptModerationView.as_view(), name = 'moderation_accept'),
    url(r'^moderation_reject/(?P<slug>[-\w]+)/?$', RejectModerationView.as_view(), name = 'moderation_rejected'),
    (r'^api/', include(v1_api.urls)),
)


urlpatterns += i18n_patterns('',
    
    url(r'^', include('nuntium.urls')),
)