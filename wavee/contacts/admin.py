from django.contrib import admin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "owner_phone",
        "contact_user",
        "contact_user_phone",
        "is_favorite",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_favorite", "created_at")
    search_fields = (
        "owner__phone_number",
        "owner__name",
        "contact_user__phone_number",
        "contact_user__name",
    )
    ordering = ("-created_at",)

    def owner_phone(self, obj):
        return obj.owner.phone_number
    owner_phone.short_description = "Owner Phone"

    def contact_user_phone(self, obj):
        return obj.contact_user.phone_number
    contact_user_phone.short_description = "Contact Phone"
