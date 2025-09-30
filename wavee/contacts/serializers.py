from rest_framework import serializers
from .models import Contact
from users.models import User

class ContactListSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source="contact_user.phone_number", read_only=True)

    class Meta:
        model = Contact
        fields = ["id", "display_name", "phone_number"]
 
class AddContactSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    display_name = serializers.CharField(max_length=255, required=False, allow_blank=True)  # 👈 new

    def validate_phone_number(self, value):
        try:
            return User.objects.get(phone_number=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this phone number does not exist.")
