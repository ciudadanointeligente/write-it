from django.contrib import admin
from mailit.models import MailItTemplate
from nuntium.models import WriteItInstance
from nuntium.admin import WriteItInstanceAdmin

class MailItTemplateInline(admin.TabularInline):
	model = MailItTemplate


admin.site.unregister(WriteItInstance)
WriteItInstanceAdmin.inlines.append(MailItTemplateInline)
admin.site.register(WriteItInstance, WriteItInstanceAdmin)

