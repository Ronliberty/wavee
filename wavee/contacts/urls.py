from django.urls import path
from .views import ContactListView, AddContactView


urlpatterns = [
    path("list/", ContactListView.as_view(), name="contact-list"),
    path("add/", AddContactView.as_view(), name="add-contact"),
]