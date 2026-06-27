from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.LandingView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("search/", views.search_view, name="search"),
]
