from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
import json

from .models import SurveyResponse
from .forms import SurveyResponseForm
from .utils import export_excel, export_csv, import_excel
from apps.core.models import SiteSettings
from apps.visits.models import FieldVisit


def survey_form_view(request):
    settings = SiteSettings.get()
    if not settings.survey_open:
        return render(request, "surveys/closed.html")

    if request.method == "POST":
        data = request.POST.copy()

        # JS sends lowercase 'true'/'false'; Django BooleanField needs 'True'/'False'
        iv = data.get("uses_internet", "").strip().lower()
        data["uses_internet"] = "True" if iv in ("true", "1", "yes") else "False"

        # JS sends JSON arrays; MultipleChoiceField expects repeated POST params
        for field in ("devices", "internet_purposes"):
            raw = data.get(field, "[]")
            try:
                vals = json.loads(raw)
            except (ValueError, TypeError):
                vals = []
            data.setlist(field, vals)

        form = SurveyResponseForm(data)
        if form.is_valid():
            response = form.save(commit=False)
            x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded:
                response.ip_address = x_forwarded.split(",")[0]
            else:
                response.ip_address = request.META.get("REMOTE_ADDR")
            response.save()
            return redirect("surveys:thank_you")
    else:
        form = SurveyResponseForm()

    visits = FieldVisit.objects.filter(is_published=True).prefetch_related("villages").order_by("day_number")
    visits_data = []
    for v in visits:
        village_list = list(v.villages.values("id", "name"))
        visits_data.append({
            "pk": v.pk,
            "label": f"Day {v.day_number} – {v.date.strftime('%b %d, %Y')}",
            "villages": village_list,
        })

    return render(request, "surveys/form.html", {
        "form": form,
        "visits_json": json.dumps(visits_data),
    })


def survey_thank_you(request):
    return render(request, "surveys/thank_you.html")


class SurveyTableView(TemplateView):
    template_name = "surveys/table.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_responses"] = SurveyResponse.objects.count()
        return ctx


def survey_table_data(request):
    """JSON endpoint for the AG-Grid / custom table."""
    qs = SurveyResponse.objects.select_related("village", "visit").all()

    # Filters
    village = request.GET.get("village")
    age = request.GET.get("age")
    education = request.GET.get("education")
    occupation = request.GET.get("occupation")
    internet = request.GET.get("internet")
    awareness = request.GET.get("awareness")
    otp = request.GET.get("otp")
    fraud = request.GET.get("fraud")
    search = request.GET.get("search", "").strip()

    if village:
        qs = qs.filter(village__slug=village)
    if age:
        qs = qs.filter(age_group=age)
    if education:
        qs = qs.filter(education=education)
    if occupation:
        qs = qs.filter(occupation=occupation)
    if internet is not None and internet != "":
        qs = qs.filter(uses_internet=(internet.lower() == "true"))
    if awareness:
        qs = qs.filter(cyber_awareness_rating=awareness)
    if otp:
        qs = qs.filter(knows_otp_rule=otp)
    if fraud:
        qs = qs.filter(faced_fraud=fraud)
    if search:
        qs = qs.filter(
            Q(village__name__icontains=search) |
            Q(fraud_description__icontains=search) |
            Q(occupation_other__icontains=search)
        )

    total = qs.count()

    # Sorting
    sort_col = request.GET.get("sort", "-created_at")
    valid_sorts = [
        "created_at", "-created_at", "village__name", "-village__name",
        "age_group", "education", "occupation", "cyber_awareness_rating"
    ]
    if sort_col in valid_sorts:
        qs = qs.order_by(sort_col)

    # Pagination
    page = int(request.GET.get("page", 1))
    per_page = int(request.GET.get("per_page", 25))
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page)

    rows = []
    for r in page_obj:
        rows.append({
            "id": r.pk,
            "submitted": r.created_at.strftime("%Y-%m-%d %H:%M"),
            "village": r.village.name if r.village else "—",
            "age_group": r.get_age_group_display(),
            "education": r.get_education_display(),
            "occupation": r.occupation_display,
            "uses_internet": r.uses_internet,
            "devices": ", ".join(r.devices_display) if r.devices else "—",
            "connection_type": r.get_connection_type_display() if r.connection_type else "—",
            "hours_per_day": r.get_hours_per_day_display() if r.hours_per_day else "—",
            "cyber_awareness": r.get_cyber_awareness_rating_display() if r.cyber_awareness_rating else "—",
            "knows_otp": r.get_knows_otp_rule_display() if r.knows_otp_rule else "—",
            "faced_fraud": r.get_faced_fraud_display() if r.faced_fraud else "—",
        })

    return JsonResponse({
        "data": rows,
        "total": total,
        "page": page,
        "pages": paginator.num_pages,
        "per_page": per_page,
    })


@login_required
def survey_export(request):
    fmt = request.GET.get("format", "excel")
    qs = SurveyResponse.objects.select_related("village").all()
    if fmt == "csv":
        return export_csv(qs)
    return export_excel(qs)


@login_required
def survey_import(request):
    if request.method == "POST" and request.FILES.get("file"):
        f = request.FILES["file"]
        result = import_excel(f)
        return JsonResponse(result)
    return JsonResponse({"error": "No file provided"}, status=400)
