from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta

def default_expiry():
    return timezone.now() + timedelta(hours=24)

class UserManager(BaseUserManager):
    def create_user(self, email, phone_number, name, passkey=None, password=None,  **extra_fields):
        if not email:
            raise ValueError("Email is required")
        
        if not phone_number:
            raise ValueError("phone number is required")
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, name=name, **extra_fields)

        if passkey:
            user.set_password(passkey)
        elif password:
            user.set_password(password)
        else:
            raise ValueError("Password or passkey is required")
        

        user.save(using=self._db)
        return user
    

    def create_superuser(self, email, phone_number, name, passkey=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, phone_number, name, passkey, **extra_fields)
    

class User(AbstractUser, PermissionsMixin):
    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
   
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number", "name"]

    objects = UserManager()

    def __str__(self):
        return self.email

class Invite(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField(unique=True, blank=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(default=default_expiry)


    def mark_used(self):
        self.is_used = True
        self.save()

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expired_at
    

    @classmethod
    def create_invite(cls, email, validity_hours=24):
        return cls.objects.create(
            email=email,
            expired_at=timezone.now() + timezone.timedelta(hours=validity_hours)
        )
    
    def __str__(self):
        return f"Invite {self.token} (used={self.is_used})"
    
        

# yourapp/models.py (append)
class InviteRecord(models.Model):
    jti = models.CharField(max_length=64, unique=True)   # track usage
    created_at = models.DateTimeField(auto_now_add=True)
    used_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    used_at = models.DateTimeField(null=True, blank=True)

    def mark_used(self, user):
        self.used_by = user
        self.used_at = timezone.now()
        self.save()
