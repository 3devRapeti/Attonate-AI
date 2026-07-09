from django.contrib import admin

from .models import ContactSalesLead, SupportRequest


@admin.register(ContactSalesLead)
class ContactSalesLeadAdmin(admin.ModelAdmin):
    list_display = ["name", "lab_name", "email", "phone_number", "created_at"]
    search_fields = ["name", "lab_name", "email", "phone_number"]
    readonly_fields = ["created_at"]


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ["__str__", "reason", "submitted_mode", "user", "created_at"]
    list_filter = ["reason", "submitted_mode"]
    search_fields = ["name", "email", "message", "user__email"]
    readonly_fields = ["created_at"]
