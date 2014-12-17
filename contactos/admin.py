from django.contrib import admin
from contactos.models import Contact, ContactType


class ContactAdmin(admin.ModelAdmin):
    actions = ['resend_errored_mails']
    search_fields = ['person__name', 'value']

    def resend_errored_mails(self, request, queryset):
        for contact in queryset:
            contact.resend_messages()
    resend_errored_mails.short_description = "Resends bounced mails"
admin.site.register(Contact, ContactAdmin)


class ContactTypeAdmin(admin.ModelAdmin):
    pass
admin.site.register(ContactType, ContactTypeAdmin)
