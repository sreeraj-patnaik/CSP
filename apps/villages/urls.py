from django.urls import path
from . import views

app_name = "villages"

urlpatterns = [
    path("", views.VillageListView.as_view(), name="list"),
    path("<slug:slug>/", views.VillageDetailView.as_view(), name="detail"),
    path("api/map-data/", views.village_map_data, name="map-data"),
]
