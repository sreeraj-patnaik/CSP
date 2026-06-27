from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .generators import generate_summary_pdf
from apps.surveys.utils import export_excel, export_csv


class ReportsView(TemplateView):
    template_name = "reports/index.html"


@login_required
def download_pdf_report(request):
    buffer = generate_summary_pdf()
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="csp_survey_report.pdf"'
    return response


@login_required
def download_excel_report(request):
    return export_excel()


@login_required
def download_csv_report(request):
    return export_csv()
