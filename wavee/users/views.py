# from rest_framework import generics, status
# from rest_framework.response import Response
# from django.utils import timezone
# from django.shortcuts import get_object_or_404
# from .models import User, Invite

# from .serializers import UserSerializer, RegisterSerializer
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.views import APIView



# # class RegisterUserView(APIView):
# #     permission_classes = [AllowAny]
# #     def post(self, request, token, *args, **kwargs):
# #         invite = get_object_or_404(Invite, token=token, is_used=False)
# #         if invite.expires_at < timezone.now():
# #             return Response({"error": "Invite token has expired."}, status=status.HTTP_400_BAD_REQUEST)
# #         serializer = UserSerializer(data=request.data)
# #         if serializer.is_valid():
# #             user = serializer.save()
# #             invite.is_used = True
# #             invite.save()
# #             return Response({"message": "User registered successfully", "user": UserSerializer(user).data},
# #                             status=status.HTTP_201_CREATED)
# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# class RegisterUserView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, token, *args, **kwargs):
#         data = request.data.copy()
#         data["token"] = token  # inject token into serializer

#         serializer = RegisterSerializer(data=data)
#         if serializer.is_valid():
#             user = serializer.save()
#             return Response(
#                 {"message": "User registered successfully", "user": UserSerializer(user).data},
#                 status=status.HTTP_201_CREATED,
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# class UserListView(generics.ListAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [IsAuthenticated]


# yourapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated

from rest_framework import status
from django.conf import settings
from .utils.invite_jwt import create_invite_jwt, decode_invite_jwt
from .serializers import RegisterSerializer, EmailLoginSerializer, CurrentUserSerializer
from django.utils import timezone
from .models import * # optional
from rest_framework_simplejwt.tokens import RefreshToken

class CreateInviteView(APIView):
    permission_classes = [IsAdminUser]  # only admins can create invites

    def post(self, request):
        """
        Request body: { "email": "invitee@example.com", "role": "writer", "expiry_hours": 48 }
        Returns frontend link.
        """
        email = request.data.get("email")
        role = request.data.get("role", "user")
        expiry = request.data.get("expiry_hours")
        token = create_invite_jwt(email=email, role=role, expiry_hours=expiry)
        frontend = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
        invite_url = f"{frontend.rstrip('/')}/auth/register?invite={token}"
        # Optionally email the invite_url here
        return Response({"invite_url": invite_url})

class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        invite_token = request.data.get("invite")
        email = request.data.get("email")
        phone = request.data.get("phone_number")
        name = request.data.get("name")
        password = request.data.get("passkey")

        if not invite_token:
            return Response({"error": "Missing invite token"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = decode_invite_jwt(invite_token)
        except jwt.ExpiredSignatureError:
            return Response({"error": "Invite expired"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Invalid invite: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Optionally: check Invite model
        invite_obj = Invite.objects.filter(email=email, is_used=False).first()
        if not invite_obj:
            return Response({"error": "No active invite found"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            email=email,
            phone_number=phone,
            name=name,
            password=password,
            
        )

        invite_obj.is_used = True
        invite_obj.save()

        return Response({"success": True, "user_id": user.id}, status=status.HTTP_201_CREATED)

    # def post(self, request):
    #     """
    #     Accepts JSON including invite token.
    #     {
    #       "invite": "<JWT>",
    #       "email": "...",
    #       "phone_number":"...",
    #       "name":"...",
    #       "passkey":"..."
    #     }
    #     """
    #     serializer = RegisterSerializer(data=request.data, context={"check_revoke": True})
    #     if not serializer.is_valid():
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     user = serializer.save()
    #     # Optionally issue auth token here (JWT for auth) and return it
    #     return Response({"message": "User registered", "user": {"id": str(user.id), "email": user.email}}, status=status.HTTP_201_CREATED)


# users/views.py


class LoginAPIView(APIView):
    def post(self, request):
        serializer = EmailLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
            }
        }, status=status.HTTP_200_OK)




class EmailLoginView(APIView):
    permission_classes = [AllowAny]

    """
    Custom login view for email + passkey authentication returning JWT.
    """

    def post(self, request):
        serializer = EmailLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
            }
        }, status=status.HTTP_200_OK)
    

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]  # JWT must be provided

    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)