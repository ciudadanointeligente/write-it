from django.contrib import admin
from mailit.models import MailItTemplate


class MailItTemplateInline(admin.ModelAdmin):
    pass


admin.site.register(MailItTemplate, MailItTemplateInline)
