from django.urls import path
from . import views

app_name = "visits"

urlpatterns = [
    path("", views.VisitListView.as_view(), name="list"),
    path("day/<int:day>/", views.VisitDetailView.as_view(), name="detail"),
]
