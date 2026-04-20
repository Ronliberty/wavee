


# yourapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
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

    def post(self, request):
        serializer = EmailLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        response = Response({
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
            }
        }, status=status.HTTP_200_OK)

        # ✅ Set cookies
        response.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=True,  # True in production (HTTPS)
            samesite="None"
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="None"
        )

        return response






class CookieTokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"error": "No refresh token"}, status=401)

        try:
            refresh = RefreshToken(refresh_token)
            access = str(refresh.access_token)

            response = Response({"message": "Token refreshed"})

            response.set_cookie(
                key="access_token",
                value=access,
                httponly=True,
                secure=True,
                samesite="None"
            )

            return response
        except Exception:
            return Response({"error": "Invalid refresh token"}, status=401)

class LogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logged out"})

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]  # JWT must be provided

    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)