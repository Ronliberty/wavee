
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/contacts/", include("contacts.urls")),
    path("api/chat/", include("chat.urls")),
    path("api/mess/", include("mess.urls"))

]


