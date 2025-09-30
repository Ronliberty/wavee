from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Contact
from .serializers import ContactListSerializer, AddContactSerializer

class ContactListView(generics.ListAPIView):
    serializer_class = ContactListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(owner=self.request.user)
    

class AddContactView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AddContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact_user = serializer.validated_data["phone_number"]
        display_name = serializer.validated_data.get("display_name", None)
        if request.user == contact_user:
            return Response({"error": "You cannot add yourself as a contact."}, status=status.HTTP_400_BAD_REQUEST)
        
        contact, created = Contact.objects.get_or_create(owner=request.user, contact_user=contact_user, defaults={"phone_number": contact_user.phone_number, "display_name": display_name})

        if not created:
            return Response({"message": "This user is already in your contacts."}, status=status.HTTP_200_OK)
        if display_name:
            contact.display_name = display_name
            contact.save
        return Response(
            {"id": contact.id, "display_name": contact.display_name, "phone_number": str(contact.phone_number)},
            status=status.HTTP_201_CREATED
        )