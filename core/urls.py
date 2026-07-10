from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("client/", views.client_home, name="client_home"),
    path("apply/", views.apply_view, name="apply"),
    path("coming-soon/", views.coming_soon_view, name="coming_soon"),
]
