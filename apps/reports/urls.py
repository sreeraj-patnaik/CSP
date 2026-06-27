from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.ReportsView.as_view(), name="index"),
    path("pdf/", views.download_pdf_report, name="pdf"),
    path("excel/", views.download_excel_report, name="excel"),
    path("csv/", views.download_csv_report, name="csv"),
]
