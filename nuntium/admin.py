from django.contrib import admin
from nuntium.models import  Message, WriteItInstance, OutboundMessage, MessageRecord, \
                            Answer, AnswerWebHook, NewAnswerNotificationTemplate, \
                            NewAnswerNotificationTemplate
from popit.models import ApiInstance, Person
from django.forms.models import BaseInlineFormSet
from mailit.models import MailItTemplate
from django_object_actions import DjangoObjectActions

class PersonInline(admin.TabularInline):
    model=Person

class MembershipInline(admin.TabularInline):
    model = WriteItInstance.persons.through

class NewAnswerNotificationTemplateAdmin(admin.TabularInline):
    model = NewAnswerNotificationTemplate

class MailItTemplateInline(admin.TabularInline):
    model = MailItTemplate


class WriteItInstanceAdmin(admin.ModelAdmin):
    inlines = [
        MembershipInline,
        NewAnswerNotificationTemplateAdmin,
        MailItTemplateInline
    ]
    exclude = ('persons',)
admin.site.register(WriteItInstance, WriteItInstanceAdmin)


class AnswerAdmin(admin.ModelAdmin):
    pass

admin.site.register(Answer, AnswerAdmin)


class AnswerInline(admin.TabularInline):
    model = Answer

class MessageAdmin(DjangoObjectActions, admin.ModelAdmin):
    change_form_template = "admin/nuntium/message/change_form.html"
    exclude = ('slug', 'moderated', 'confirmated')
    inlines = [
        AnswerInline
    ]
    def moderate_this(self, request, obj):
        obj.moderate()
    moderate_this.label = "Moderate"  # optional
    moderate_this.short_description = "Moderate this message"  # optional

    objectactions = ('moderate_this', )

admin.site.register(Message, MessageAdmin)

class AnswerWebHookAdmin(admin.ModelAdmin):
    pass
admin.site.register(AnswerWebHook, AnswerWebHookAdmin)

class OutboundMessageAdmin(admin.ModelAdmin):
    pass
admin.site.register(OutboundMessage, OutboundMessageAdmin)

class MessageRecordAdmin(admin.ModelAdmin):
    pass
admin.site.register(MessageRecord, MessageRecordAdmin)

class ApiInstanceAdmin(admin.ModelAdmin):
    pass
admin.site.register(ApiInstance, ApiInstanceAdmin)

class PersonAdmin(admin.ModelAdmin):
    pass
admin.site.register(Person, PersonAdmin)

class NewAnswerNotificationTemplateAdmin(admin.ModelAdmin):
    pass
admin.site.register(NewAnswerNotificationTemplate, NewAnswerNotificationTemplateAdmin)

