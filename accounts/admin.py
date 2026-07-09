from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import ClientProfile, Profile, User


class UserAdmin(BaseUserAdmin):
    ordering = ["email"]
    list_display = ["email", "phone_number", "account_type", "is_staff", "is_active", "date_joined"]
    search_fields = ["email", "phone_number"]
    list_filter = ["account_type", "is_staff", "is_active"]
    fieldsets = (
        (None, {"fields": ("email", "phone_number", "password")}),
        ("Account type", {"fields": ("account_type",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "phone_number", "account_type", "password1", "password2")}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "display_name", "job_title", "rating", "notifications_paused", "created_at"]
    search_fields = ["display_name", "user__email", "job_title"]
    list_filter = ["visa_status", "notifications_paused"]


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "full_name", "company_name", "sector", "country", "created_at"]
    search_fields = ["full_name", "company_name", "user__email"]
    list_filter = ["sector", "company_size"]


admin.site.register(User, UserAdmin)
