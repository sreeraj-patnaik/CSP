from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.db.models import Prefetch
from .models import Village, VillageObservation
from apps.surveys.models import SurveyResponse
from apps.visits.models import FieldVisit, VisitMedia
from apps.gallery.models import Photo
import json


class VillageListView(ListView):
    model = Village
    template_name = "villages/list.html"
    context_object_name = "villages"
    queryset = Village.objects.filter(is_active=True).order_by("order")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        villages = list(ctx["villages"])
        thumbnail_map = self._build_card_thumbnail_map(villages)

        for village in villages:
            thumbnail_url = thumbnail_map.get(village.pk)
            if not thumbnail_url and village.thumbnail:
                thumbnail_url = village.thumbnail.url
            if not thumbnail_url and village.hero_image:
                thumbnail_url = village.hero_image.url
            village.card_thumbnail_url = thumbnail_url

        ctx["villages"] = villages
        # Build village summary map data
        map_data = []
        for v in villages:
            if v.latitude and v.longitude:
                map_data.append({
                    "name": v.name,
                    "slug": v.slug,
                    "lat": float(v.latitude),
                    "lng": float(v.longitude),
                    "population": v.population or 0,
                    "survey_count": v.survey_count,
                    "internet_pct": v.internet_usage_pct,
                    "color": v.color_accent,
                })
        ctx["map_data_json"] = json.dumps(map_data)
        return ctx

    def _build_card_thumbnail_map(self, villages):
        village_ids = [v.pk for v in villages]
        if not village_ids:
            return {}

        thumbnail_map = {}

        # Prefer photos from field visits because they best match the user's request.
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

        # Fall back to direct village-linked gallery photos if a village has no visit photo yet.
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

        return thumbnail_map


class VillageDetailView(DetailView):
    model = Village
    template_name = "villages/detail.html"
    context_object_name = "village"

    def get_queryset(self):
        return Village.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        village = self.object
        ctx["visits"] = FieldVisit.objects.filter(villages=village).prefetch_related("villages").order_by("-date")
        # Photos from the Photo model (linked by village)
        ctx["photos"] = Photo.objects.filter(village=village).order_by("-created_at")[:20]
        # Photos from VisitMedia (linked by visit → village)
        ctx["vm_photos"] = VisitMedia.objects.filter(
            media_type="photo", visit__villages=village
        ).select_related("visit").order_by("-visit__date", "order")[:20]
        ctx["observations"] = VillageObservation.objects.filter(village=village).order_by("order")
        ctx["survey_stats"] = self._get_survey_stats(village)
        ctx["all_villages"] = Village.objects.filter(is_active=True).exclude(pk=village.pk)
        return ctx

    def _get_survey_stats(self, village):
        qs = SurveyResponse.objects.filter(village=village)
        total = qs.count()
        if total == 0:
            return {"total": 0}
        internet_users = qs.filter(uses_internet=True).count()
        fraud_exp = qs.filter(faced_fraud="yes").count()
        otp_aware = qs.filter(knows_otp_rule="yes").count()
        return {
            "total": total,
            "internet_users": internet_users,
            "internet_pct": round((internet_users / total) * 100, 1),
            "fraud_exp": fraud_exp,
            "fraud_pct": round((fraud_exp / total) * 100, 1),
            "otp_aware": otp_aware,
            "otp_pct": round((otp_aware / total) * 100, 1),
        }


def village_map_data(request):
    villages = Village.objects.filter(is_active=True)
    data = []
    for v in villages:
        if v.latitude and v.longitude:
            data.append({
                "name": v.name,
                "slug": v.slug,
                "lat": float(v.latitude),
                "lng": float(v.longitude),
                "population": v.population,
                "survey_count": v.survey_count,
                "internet_pct": v.internet_usage_pct,
                "color": v.color_accent,
                "url": v.get_absolute_url(),
            })
    return JsonResponse({"villages": data})
