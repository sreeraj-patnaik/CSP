from django.urls import path
from . import views

app_name = "api-analytics"

urlpatterns = [
    path("data/", views.analytics_data, name="data"),
    path("insights/", views.auto_insights_view, name="insights"),
]
