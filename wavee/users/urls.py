

from django.urls import path
from .views import CreateInviteView, RegisterUserView, EmailLoginView, CurrentUserView, CookieTokenRefreshView, LogoutView
# from rest_framework_simplejwt.views import TokenBlacklistView

urlpatterns = [
    path("invites/create/", CreateInviteView.as_view(), name="create-invite"),
    path("register/", RegisterUserView.as_view(), name="register-with-invite"),
    path("login/", EmailLoginView.as_view(), name="email-login"),
    path("me/", CurrentUserView.as_view(), name="current-user"),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/refresh/", CookieTokenRefreshView.as_view()),


]


