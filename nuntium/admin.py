from django.contrib import admin
from nuntium.models import Message, WriteItInstance, OutboundMessage, MessageRecord, Answer, AnswerWebHook, NewAnswerNotificationTemplate
from popit.models import ApiInstance, Person
from django.forms.models import BaseInlineFormSet
from mailit.models import MailItTemplate

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



# class AnswerInlineFormset(BaseInlineFormSet):
#     def __init__(self, *args, **kwargs):
#         super(AnswerInlineFormset, self).__init__(*args, **kwargs)

class AnswerAdmin(admin.ModelAdmin):
    pass

admin.site.register(Answer, AnswerAdmin)


class AnswerInline(admin.TabularInline):
    model = Answer
    # formset = AnswerInlineFormset

class MessageAdmin(admin.ModelAdmin):
    exclude = ('slug', )
    inlines = [
        AnswerInline
    ]
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

