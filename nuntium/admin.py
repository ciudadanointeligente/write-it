from django.contrib import admin
from .models import  Message, WriteItInstance, OutboundMessage, MessageRecord, \
                            Answer, AnswerWebHook, NewAnswerNotificationTemplate, \
                            NewAnswerNotificationTemplate
from popit.models import ApiInstance, Person
from django.forms.models import BaseInlineFormSet
from mailit.models import MailItTemplate
from django_object_actions import DjangoObjectActions
from django.db.models import Q
from .forms import WriteItInstanceCreateFormPopitUrl

class PersonInline(admin.TabularInline):
    model=Person

class MembershipInline(admin.TabularInline):
    model = WriteItInstance.persons.through

class NewAnswerNotificationTemplateAdmin(admin.TabularInline):
    model = NewAnswerNotificationTemplate

class MailItTemplateInline(admin.TabularInline):
    model = MailItTemplate


class WriteItInstanceAdmin(admin.ModelAdmin):
    form = WriteItInstanceCreateFormPopitUrl
    inlines = [
        MembershipInline,
        NewAnswerNotificationTemplateAdmin,
        MailItTemplateInline
    ]
    exclude = ('persons',)

    def save_model(self, request, obj, form, change):
        super(WriteItInstanceAdmin, self).save_model(request, obj, form, change)
        form.relate_with_people()


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
    actions=['moderate']
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

