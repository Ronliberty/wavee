
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/contacts/", include("contacts.urls")),
    path("api/chat/", include("chat.urls")),
    path("api/mess/", include("mess.urls")),
    path("api/auth/jwt/refresh/", TokenRefreshView.as_view())

]

if settings.DEBUG:  # only in dev
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
