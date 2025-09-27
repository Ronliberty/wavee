# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from .models import Invite

# User = get_user_model()


# class UserSerializer(serializers.ModelSerializer):
#     """Serializer to return basic user info (no password)."""
#     class Meta:
#         model = User
#         fields = ["id", "email", "phone_number", "name", "is_active", "date_joined"]
#         read_only_fields = ["id", "is_active", "date_joined"]


# class RegisterSerializer(serializers.Serializer):
#     token = serializers.UUIDField()
#     email = serializers.EmailField()
#     phone_number = serializers.CharField(max_length=15)
#     name = serializers.CharField(max_length=255)
#     passkey = serializers.CharField(write_only=True, min_length=6)

#     def validate_token(self, value):
#         try:
#             invite = Invite.objects.get(token=value, is_used=False)
#         except Invite.DoesNotExist:
#             raise serializers.ValidationError("Invalid or already used invite token.")

#         if not invite.is_valid():
#             raise serializers.ValidationError("Invite token has expired.")

#         return value

#     def create(self, validated_data):
#         token = validated_data.pop("token")
#         invite = Invite.objects.get(token=token)

#         # Mark invite used
#         invite.mark_used()

#         # Create user
#         user = User.objects.create_user(
#             email=validated_data["email"],
#             phone_number=validated_data["phone_number"],
#             name=validated_data["name"],
#             password=validated_data["passkey"],  # ✅ must use password not passkey
#         )
#         return user


# yourapp/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .utils.invite_jwt import decode_invite_jwt
from .models import * # optional

from django.contrib.auth import authenticate
User = get_user_model()

class RegisterSerializer(serializers.Serializer):
    invite = serializers.CharField(write_only=True)   # the JWT token string
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=15)
    name = serializers.CharField(max_length=255)
    passkey = serializers.CharField(write_only=True, min_length=6)

    def validate_invite(self, value):
        try:
            payload = decode_invite_jwt(value)
        except Exception as exc:
            raise serializers.ValidationError("Invalid or expired invite token.") from exc

        # Optional: If invite was targeted to an email, ensure it matches provided email (optional but recommended)
        invite_email = payload.get("email")
        if invite_email and invite_email.lower() != self.initial_data.get("email", "").lower():
            raise serializers.ValidationError("Invite email does not match provided email.")

        # Optional: prevent reuse if using InviteRecord
        jti = payload.get("jti")
        if jti and hasattr(self, "context") and self.context.get("check_revoke", True):
            if InviteRecord.objects.filter(jti=jti, used_at__isnull=False).exists():
                raise serializers.ValidationError("Invite token has already been used.")

        # Save payload into validated_data for create() to use
        self._invite_payload = payload
        return value

    def create(self, validated_data):
        invite_token = validated_data.pop("invite")
        payload = getattr(self, "_invite_payload", None)
        # create user
        user = User.objects.create_user(
            email=validated_data["email"],
            phone_number=validated_data["phone_number"],
            name=validated_data["name"],
            password=validated_data["passkey"],
        )
        # Optionally mark invite record used (if using InviteRecord)
        if payload:
            jti = payload.get("jti")
            if jti:
                InviteRecord.objects.update_or_create(jti=jti, defaults={"used_by": user, "used_at": timezone.now()})
        return user


# users/serializers.py
class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    passkey = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        passkey = attrs.get("passkey")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        if not user.check_password(passkey):
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User is inactive")

        attrs["user"] = user
        return attrs
    

class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "phone_number", "date_joined"]