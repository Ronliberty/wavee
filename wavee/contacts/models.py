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

    class Meta:
        unique_together = ("owner", "contact_user")

    def __str__(self):
        return f"{self.owner} has {self.contact_user} in contacts"
    

