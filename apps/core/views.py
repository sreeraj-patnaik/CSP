from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Count, Q, Sum

from django.db.models import Prefetch

from apps.villages.models import Village
from apps.visits.models import FieldVisit, VisitMedia
from apps.surveys.models import SurveyResponse
from apps.team.models import TeamMember
from apps.gallery.models import Photo
from .models import SiteSettings


def _annotate_village_thumbnails(villages):
    """Attach card_thumbnail_url to each village by pulling real photos from visits/gallery."""
    village_ids = [v.pk for v in villages]
    if not village_ids:
        return

    thumbnail_map = {}

    visit_qs = (
        FieldVisit.objects.filter(villages__in=village_ids)
        .prefetch_related(
            "villages",
            Prefetch(
                "media",
                queryset=VisitMedia.objects.filter(media_type="photo").order_by("order", "-created_at"),
            ),
        )
        .order_by("-date", "day_number")
    )
    for visit in visit_qs:
        for media in visit.media.all():
            if not media.file:
                continue
            for village in visit.villages.all():
                if village.pk in village_ids and village.pk not in thumbnail_map:
                    thumbnail_map[village.pk] = media.file.url

    photo_qs = (
        Photo.objects.filter(village_id__in=village_ids)
        .select_related("village")
        .order_by("-is_featured", "-date_taken", "-created_at")
    )
    for photo in photo_qs:
        if photo.village_id in thumbnail_map:
            continue
        image = photo.thumbnail.url if photo.thumbnail else photo.image.url if photo.image else None
        if image:
            thumbnail_map[photo.village_id] = image

    for village in villages:
        url = thumbnail_map.get(village.pk)
        if not url and village.thumbnail:
            url = village.thumbnail.url
        if not url and village.hero_image:
            url = village.hero_image.url
        village.card_thumbnail_url = url


class LandingView(TemplateView):
    template_name = "landing/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        villages = list(Village.objects.filter(is_active=True).order_by("order"))
        _annotate_village_thumbnails(villages)
        ctx["villages"] = villages
        ctx["total_villages"] = Village.objects.filter(is_active=True).count()
        ctx["total_visits"] = FieldVisit.objects.count()
        ctx["total_responses"] = SurveyResponse.objects.count()
        ctx["total_volunteers"] = TeamMember.objects.filter(role__in=["member", "lead", "volunteer"]).count()
        ctx["total_people_reached"] = (
            Village.objects.filter(is_active=True)
            .aggregate(total=Sum("population"))["total"] or 0
        )
        ctx["total_awareness_sessions"] = FieldVisit.objects.count()
        ctx["recent_visits"] = FieldVisit.objects.prefetch_related("villages").order_by("-date")[:3]
        featured = list(Photo.objects.filter(is_featured=True).order_by("-created_at")[:12])
        if not featured:
            # Fall back to VisitMedia photos when no Photo model entries are marked featured
            featured = list(VisitMedia.objects.filter(media_type="photo").select_related("visit").order_by("-visit__date", "order")[:12])
        ctx["featured_photos"] = featured
        ctx["featured_are_vm"] = featured and not hasattr(featured[0], "image")
        site_settings = SiteSettings.get()
        ctx["site_settings"] = site_settings
        ctx["mentor_name"] = site_settings.mentor_name or "Dr. R. Rajender"
        ctx["college_name"] = site_settings.college_name or "Lendi Institute of Engineering and Technology"
        ctx["academic_year"] = site_settings.academic_year

        # Real survey statistics for community pulse section
        total = SurveyResponse.objects.count()
        if total:
            internet_count = SurveyResponse.objects.filter(uses_internet=True).count()
            ctx["internet_pct"] = round(internet_count * 100 / total)
            high_aware = SurveyResponse.objects.filter(
                cyber_awareness_rating__in=["high", "very_high"]
            ).count()
            ctx["high_awareness_pct"] = round(high_aware * 100 / total)
            fraud_count = SurveyResponse.objects.filter(faced_fraud="yes").count()
            ctx["fraud_count"] = fraud_count
            otp_aware = SurveyResponse.objects.filter(knows_otp_rule="yes").count()
            ctx["otp_aware_pct"] = round(otp_aware * 100 / total)
        else:
            ctx["internet_pct"] = None
            ctx["high_awareness_pct"] = None
            ctx["fraud_count"] = None
            ctx["otp_aware_pct"] = None
        return ctx


class AboutView(TemplateView):
    template_name = "about/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["team"] = TeamMember.objects.filter(is_active=True).order_by("order")
        ctx["mentor"] = TeamMember.objects.filter(role="mentor", is_active=True).first()
        ctx["visits"] = FieldVisit.objects.prefetch_related("villages").order_by("date")
        ctx["villages"] = Village.objects.filter(is_active=True).order_by("order")
        ctx["total_responses"] = SurveyResponse.objects.count()
        ctx["total_villages"] = Village.objects.filter(is_active=True).count()
        site_settings = SiteSettings.get()
        ctx["mentor_name"] = site_settings.mentor_name or "Dr. R. Rajender"
        ctx["college_name"] = site_settings.college_name or "Lendi Institute of Engineering and Technology"
        ctx["academic_year"] = site_settings.academic_year
        return ctx


def search_view(request):
    q = request.GET.get("q", "").strip()
    results = {"villages": [], "visits": [], "surveys": [], "photos": []}
    if len(q) >= 2:
        results["villages"] = list(
            Village.objects.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            ).values("id", "name", "slug")[:5]
        )
        results["visits"] = list(
            FieldVisit.objects.filter(
                Q(title__icontains=q) | Q(summary__icontains=q)
            ).values("id", "title", "date", "day_number")[:5]
        )
        results["photos"] = list(
            Photo.objects.filter(
                Q(caption__icontains=q) | Q(tags__icontains=q)
            ).values("id", "caption", "image")[:4]
        )
    return JsonResponse({"query": q, "results": results})


def handler404(request, exception):
    return render(request, "errors/404.html", status=404)


def handler500(request):
    return render(request, "errors/500.html", status=500)
