from django.db import models
from django.conf import settings

from phonenumber_field.modelfields import PhoneNumberField

class Contact(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contacts')
    contact_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='as_contact')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_favorite = models.BooleanField(default=False)
    phone_number = PhoneNumberField()
    display_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ("owner", "contact_user")

    def __str__(self):
        return f"{self.owner} saved {self.contact_user} as {self.display_name or self.contact_user.username}"
    

