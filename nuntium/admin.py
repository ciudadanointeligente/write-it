from django.contrib import admin
from nuntium.models import Message, WriteItInstance, OutboundMessage, MessageRecord
from popit.models import ApiInstance, Person
from contactos.models import Contact, ContactType

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

class MessageAdmin(admin.ModelAdmin):
    pass
admin.site.register(Message, MessageAdmin)

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