from django.contrib import admin
from nuntium.models import Message, WriteItInstance, OutboundMessage, MessageRecord, Answer, AnswerWebHook
from popit.models import ApiInstance, Person
from contactos.models import Contact, ContactType
from django.forms.models import BaseInlineFormSet

class PersonInline(admin.TabularInline):
	model=Person

class MembershipInline(admin.TabularInline):
    model = WriteItInstance.persons.through

class WriteItInstanceAdmin(admin.ModelAdmin):
    inlines = [
    	MembershipInline,
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

class ContactAdmin(admin.ModelAdmin):
	pass
admin.site.register(Contact, ContactAdmin)

class ContactTypeAdmin(admin.ModelAdmin):
	pass
admin.site.register(ContactType, ContactTypeAdmin)