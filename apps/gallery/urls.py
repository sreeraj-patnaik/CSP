from django.urls import path
from . import views

app_name = "gallery"

urlpatterns = [
    path("", views.GalleryView.as_view(), name="index"),
    path("data/", views.gallery_data, name="data"),
    path("map/", views.gallery_map_data, name="map-data"),
]
