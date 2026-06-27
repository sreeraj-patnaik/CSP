from django.urls import path
from . import views

app_name = "surveys"

urlpatterns = [
    path("", views.survey_form_view, name="form"),
    path("thank-you/", views.survey_thank_you, name="thank_you"),
    path("data/", views.SurveyTableView.as_view(), name="table"),
    path("data/json/", views.survey_table_data, name="table-data"),
    path("export/", views.survey_export, name="export"),
    path("import/", views.survey_import, name="import"),
]
