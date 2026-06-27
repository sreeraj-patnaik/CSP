from django.urls import path
from . import api_views

app_name = "api-surveys"

urlpatterns = [
    path("", api_views.SurveyResponseListAPIView.as_view(), name="list"),
    path("stats/", api_views.SurveyStatsAPIView.as_view(), name="stats"),
]
