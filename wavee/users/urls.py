

# yourapp/urls.py
from django.urls import path
from .views import CreateInviteView, RegisterUserView, EmailLoginView, CurrentUserView, CookieTokenRefreshView
from rest_framework_simplejwt.views import TokenBlacklistView

urlpatterns = [
    path("invites/create/", CreateInviteView.as_view(), name="create-invite"),
    path("register/", RegisterUserView.as_view(), name="register-with-invite"),
    path("login/", EmailLoginView.as_view(), name="email-login"),
    path("me/", CurrentUserView.as_view(), name="current-user"),
    path("auth/logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("auth/refresh/", CookieTokenRefreshView.as_view()),


]


