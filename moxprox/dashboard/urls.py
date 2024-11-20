from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("refresh/", views.refresh, name="refresh"),
    path("manage_domain/", views.manage_domain, name="manage_domain"),
    path("create_vm/", views.create_vm, name="create_vm"),
    path("migrate_vm/", views.migrate_vm, name="migrate_vm")
]