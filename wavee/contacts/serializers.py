from rest_framework import serializers
from .models import Contact
from users.models import User


class ContactSerializer(serializers.ModelSerializer):
    contact_user_details = serializers.SerializerMethodField()


    class Meta:
        model = Contact
        fields = ['id', 'owner', 'contact_user', 'contact_user_details', 'created_at', 'updated_at', 'is_favorite']

    def get_contact_user_details(self, obj):
            return {
                "id": obj.contact_user.id,
                "email": obj.contact_user.email,
                "name": obj.contact_user.name,
                "phone_number": obj.contact_user.phone_number,
            }
        

class AddContactSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value):
        try:
            return User.objects.get(phone_number=value)
        except User.DoesNotExists:
            raise serializers.ValidationError("User with this phone number does not exist.")