# from django.urls import path
# from .views import RegisterUserView, UserListView

# urlpatterns = [
#     path("register/<uuid:token>/", RegisterUserView.as_view(), name="register-user"),
#     path("all/", UserListView.as_view(), name="user-list"),  # For testing/admin only
# ]


# yourapp/urls.py
from django.urls import path
from .views import CreateInviteView, RegisterUserView, EmailLoginView, CurrentUserView


urlpatterns = [
    path("invites/create/", CreateInviteView.as_view(), name="create-invite"),
    path("register/", RegisterUserView.as_view(), name="register-with-invite"),
    path("login/", EmailLoginView.as_view(), name="email-login"),
    path("me/", CurrentUserView.as_view(), name="current-user"),
    
  
]


