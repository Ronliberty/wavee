from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from .models import User, Invite
from .utils.invite_jwt import create_invite_jwt

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ("email", "is_used", "created_at", "expired_at", "invite_link")
    readonly_fields = ("token", "created_at")

    def invite_link(self, obj):
        if obj.email and not obj.is_used:
            token = create_invite_jwt(email=obj.email)
            url = f"{settings.FRONTEND_URL}/invite?invite={token}"
            return format_html("<a href='{}' target='_blank'>{}</a>", url, url)
        return "—"

    invite_link.short_description = "Invite Link"


# users/admin.py


class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("email", "name", "phone_number", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "name", "phone_number")
    ordering = ("email",)
    readonly_fields = ("date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "phone_number", "name", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("date_joined",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "phone_number", "name", "password1", "password2", "is_staff", "is_active")}
        ),
    )

admin.site.register(User, UserAdmin)
