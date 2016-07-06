from django.contrib import admin
from instance.models import WriteItInstanceConfig
from .models import Message, OutboundMessage, MessageRecord, \
    Answer, AnswerWebHook, NewAnswerNotificationTemplate, \
    ConfirmationTemplate

from instance.models import WriteItInstance
from popit.models import ApiInstance, Person
from mailit.models import MailItTemplate
from django_object_actions import DjangoObjectActions
from nuntium.forms import WriteItInstanceCreateFormPopitUrl


class PersonInline(admin.TabularInline):
    model = Person


class MembershipInline(admin.TabularInline):
    model = WriteItInstance.persons.through


class NewAnswerNotificationTemplateAdmin(admin.TabularInline):
    model = NewAnswerNotificationTemplate


class MailItTemplateInline(admin.TabularInline):
    model = MailItTemplate


class WriteItInstanceConfigInline(admin.StackedInline):
    model = WriteItInstanceConfig


class WriteItInstanceAdmin(admin.ModelAdmin):
    model = WriteItInstance
    inlines = [
        WriteItInstanceConfigInline,
        MembershipInline,
        NewAnswerNotificationTemplateAdmin,
        MailItTemplateInline
    ]
    fields = ('owner', 'name', )


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


class NeedingModerationMessage(Message):
    class Meta:
        proxy = True


class NonModeratedMessageAdmin(MessageAdmin):
    def get_queryset(self, request):
        qs = Message.moderation_required_objects.all()
        return qs
    actions = ['moderate']

    def moderate(self, request, queryset):
        for message in queryset:
            message.moderate()
    #moderate.short_description(_("Mark the selected messages as moderated"))

admin.site.register(NeedingModerationMessage, NonModeratedMessageAdmin)


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


class ConfirmationTemplateAdmin(admin.ModelAdmin):
    pass
admin.site.register(ConfirmationTemplate, ConfirmationTemplateAdmin)
