from django.urls import path
from . import views

app_name = "api-gallery"

urlpatterns = [
    path("", views.gallery_data, name="list"),
    path("map/", views.gallery_map_data, name="map"),
]
