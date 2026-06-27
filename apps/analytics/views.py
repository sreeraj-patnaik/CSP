from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.core.cache import cache
from . import insights as ins


class AnalyticsDashboardView(TemplateView):
    template_name = "analytics/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from apps.surveys.models import SurveyResponse
        from apps.villages.models import Village
        ctx["total_responses"] = SurveyResponse.objects.count()
        ctx["villages"] = Village.objects.filter(is_active=True)
        return ctx


def analytics_data(request):
    """Single endpoint returning all chart data as JSON. Cached for 5 min."""
    village = request.GET.get("village", "all")
    cache_key = f"analytics_data_{village}"
    data = cache.get(cache_key)
    if not data:
        data = {
            "village_comparison": ins.village_comparison(village),
            "age_vs_internet": ins.age_vs_internet(),
            "education_vs_awareness": ins.education_vs_awareness(),
            "occupation_vs_awareness": ins.occupation_vs_awareness(),
            "device_distribution": ins.device_distribution(),
            "purposes": ins.internet_purposes_distribution(),
            "fraud_by_village": ins.fraud_experience_by_village(),
            "otp_awareness": ins.otp_awareness_distribution(),
            "daily_trend": ins.daily_submission_trend(),
            "awareness_heatmap": ins.awareness_heatmap(),
            "connection_types": ins.connection_type_distribution(),
            "hours_distribution": ins.hours_per_day_distribution(),
        }
        cache.set(cache_key, data, 300)
    return JsonResponse(data)


def auto_insights_view(request):
    cache_key = "auto_insights"
    result = cache.get(cache_key)
    if not result:
        result = ins.generate_auto_insights()
        cache.set(cache_key, result, 300)
    return JsonResponse({"insights": result})
