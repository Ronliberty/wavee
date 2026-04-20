from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
import uuid


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Owner (who saved the contact)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contacts"
    )

    # Phone number is the SOURCE OF TRUTH
    phone_number = PhoneNumberField()

    # Optional link to a registered user
    contact_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="saved_as_contact"
    )

    # Custom name (what John calls Eric)
    display_name = models.CharField(max_length=255, blank=True, null=True)

    is_favorite = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("owner", "phone_number")

    def __str__(self):
        return f"{self.owner} → {self.display_name or self.phone_number}"