from django.contrib import admin
from nuntium.models import Message, WriteItInstance, OutboundMessage, MessageRecord

class WriteItInstanceAdmin(admin.ModelAdmin):
    pass
admin.site.register(WriteItInstance, WriteItInstanceAdmin)