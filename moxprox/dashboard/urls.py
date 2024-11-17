from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("refresh/", views.refresh, name="refresh"),
    path("manage_domain/", views.start_domain, name="manage_domain"),
]