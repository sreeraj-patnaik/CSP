from django.urls import path
from . import api_views

app_name = "api-villages"

urlpatterns = [
    path("", api_views.VillageListAPIView.as_view(), name="list"),
    path("<slug:slug>/", api_views.VillageDetailAPIView.as_view(), name="detail"),
    path("map/", api_views.VillageMapAPIView.as_view(), name="map"),
]
