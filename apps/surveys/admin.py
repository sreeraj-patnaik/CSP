from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.contrib import messages
from django.shortcuts import render

from .models import SurveyResponse
from .utils import export_excel, export_csv, import_excel


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    change_list_template = "admin/surveys/surveyresponse/change_list.html"
    list_display = (
        "id", "village", "age_group_badge", "education", "occupation",
        "internet_badge", "awareness_badge", "fraud_badge", "is_imported", "created_at"
    )
    list_filter = (
        "village", "age_group", "education", "occupation",
        "uses_internet", "cyber_awareness_rating", "faced_fraud", "knows_otp_rule",
        "is_imported",
    )
    search_fields = ("fraud_description", "occupation_other", "import_source")
    readonly_fields = ("created_at", "updated_at", "ip_address", "is_imported", "import_source")
    actions = ["export_as_excel", "export_as_csv"]

    fieldsets = (
        ("Demographics", {
            "fields": ("village", "age_group", "education", "occupation", "occupation_other"),
        }),
        ("Internet Usage", {
            "fields": (
                "uses_internet", "devices", "device_other",
                "connection_type", "connection_other",
                "hours_per_day", "internet_purposes", "purpose_other",
            ),
        }),
        ("Cyber Awareness", {
            "fields": ("cyber_awareness_rating", "knows_otp_rule", "faced_fraud", "fraud_description"),
        }),
        ("Metadata", {
            "fields": ("visit", "ip_address", "is_imported", "import_source", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "import-google-forms/",
                self.admin_site.admin_view(self.import_view),
                name="surveys_surveyresponse_import",
            ),
        ]
        return custom + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["import_url"] = reverse("admin:surveys_surveyresponse_import")
        return super().changelist_view(request, extra_context=extra_context)

    def import_view(self, request):
        if request.method == "POST":
            uploaded = request.FILES.get("file")
            if not uploaded:
                messages.error(request, "No file selected.")
                return HttpResponseRedirect(request.path)

            result = import_excel(uploaded, source_name=uploaded.name)
            created = result["created"]
            errs    = result["errors"]
            total   = result["total_rows"]

            if created:
                messages.success(
                    request,
                    f"Imported {created} of {total} responses successfully."
                )
            if errs:
                for e in errs[:10]:
                    messages.warning(request, e)
                if len(errs) > 10:
                    messages.warning(request, f"… and {len(errs) - 10} more errors.")

            return HttpResponseRedirect(
                reverse("admin:surveys_surveyresponse_changelist")
            )

        from .utils import (
            COL_VILLAGE, COL_AGE, COL_EDUCATION, COL_OCCUPATION,
            COL_INTERNET, COL_DEVICES, COL_DEV_OTHER, COL_CONNECTION,
            COL_HOURS, COL_PURPOSES, COL_PUR_OTHER, COL_AWARENESS,
            COL_OTP, COL_FRAUD, COL_FRAUD_DESC, COL_TIMESTAMP,
        )
        columns = [
            (COL_TIMESTAMP,   "created_at (backdated)"),
            (COL_VILLAGE,     "village"),
            (COL_AGE,         "age_group"),
            (COL_EDUCATION,   "education"),
            (COL_OCCUPATION,  "occupation"),
            (COL_INTERNET,    "uses_internet"),
            (COL_DEVICES,     "devices [ ]"),
            (COL_DEV_OTHER,   "device_other"),
            (COL_CONNECTION,  "connection_type"),
            (COL_HOURS,       "hours_per_day"),
            (COL_PURPOSES,    "internet_purposes [ ]"),
            (COL_PUR_OTHER,   "purpose_other"),
            (COL_AWARENESS,   "cyber_awareness_rating"),
            (COL_OTP,         "knows_otp_rule"),
            (COL_FRAUD,       "faced_fraud"),
            (COL_FRAUD_DESC,  "fraud_description"),
        ]
        context = {
            **self.admin_site.each_context(request),
            "title": "Import Survey Responses from Google Forms",
            "opts": self.model._meta,
            "columns": columns,
        }
        return render(request, "admin/surveys/import_form.html", context)

    # ── Badges ────────────────────────────────────────────────────────────────

    def age_group_badge(self, obj):
        return obj.get_age_group_display()
    age_group_badge.short_description = "Age"

    def internet_badge(self, obj):
        color = "#10B981" if obj.uses_internet else "#94A3B8"
        label = "Yes" if obj.uses_internet else "No"
        return format_html('<span style="color: {}; font-weight: 600;">{}</span>', color, label)
    internet_badge.short_description = "Internet"

    def awareness_badge(self, obj):
        colors = {
            "very_low": "#EF4444", "low": "#F97316",
            "moderate": "#F59E0B", "high": "#22C55E", "very_high": "#10B981"
        }
        color = colors.get(obj.cyber_awareness_rating, "#94A3B8")
        label = obj.get_cyber_awareness_rating_display() if obj.cyber_awareness_rating else "—"
        return format_html('<span style="color: {}; font-weight: 600;">{}</span>', color, label)
    awareness_badge.short_description = "Awareness"

    def fraud_badge(self, obj):
        colors = {"yes": "#EF4444", "no": "#10B981", "not_sure": "#F59E0B"}
        color = colors.get(obj.faced_fraud, "#94A3B8")
        label = obj.get_faced_fraud_display() if obj.faced_fraud else "—"
        return format_html('<span style="color: {};">{}</span>', color, label)
    fraud_badge.short_description = "Fraud"

    # ── Export actions ────────────────────────────────────────────────────────

    def export_as_excel(self, request, queryset):
        return export_excel(queryset)
    export_as_excel.short_description = "Export selected as Excel"

    def export_as_csv(self, request, queryset):
        return export_csv(queryset)
    export_as_csv.short_description = "Export selected as CSV"
