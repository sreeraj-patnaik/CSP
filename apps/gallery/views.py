from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.db.models import Q
from .models import Photo
from apps.villages.models import Village
from apps.visits.models import VisitMedia
import json


class GalleryView(TemplateView):
    template_name = "gallery/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["villages"] = Village.objects.filter(is_active=True)
        ctx["categories"] = Photo.CATEGORY_CHOICES
        ctx["total_photos"] = Photo.objects.count() + VisitMedia.objects.filter(media_type="photo").count()
        return ctx


def gallery_data(request):
    """AJAX endpoint returning filtered photo data (Photo model + VisitMedia photos)."""
    village = request.GET.get("village")
    category = request.GET.get("category")
    search = request.GET.get("search", "").strip()

    photos = []

    # ── Photo model (primary, rich metadata) ──────────────────────────────────
    qs = Photo.objects.select_related("village", "visit")
    if village and village != "all":
        qs = qs.filter(village__slug=village)
    if category and category != "all":
        qs = qs.filter(category=category)
    if search:
        qs = qs.filter(Q(caption__icontains=search) | Q(tags__icontains=search))

    for p in qs[:200]:
        photos.append({
            "id": f"p{p.pk}",
            "src": p.image.url,
            "thumb": p.thumbnail.url if p.thumbnail else p.image.url,
            "caption": p.caption,
            "village": p.village.name if p.village else "",
            "village_slug": p.village.slug if p.village else "",
            "category": p.category,
            "category_label": p.get_category_display(),
            "date": p.date_taken.strftime("%Y-%m-%d") if p.date_taken else "",
            "lat": float(p.latitude) if p.latitude else None,
            "lng": float(p.longitude) if p.longitude else None,
            "tags": p.tags_list,
            "width": p.width or 800,
            "height": p.height or 600,
            "is_featured": p.is_featured,
        })

    # ── VisitMedia photos (legacy / uploaded via visit admin) ─────────────────
    # Skip if filtering by category (VisitMedia has no category)
    if not category or category == "all":
        vm_qs = VisitMedia.objects.filter(media_type="photo").select_related("visit")
        if search:
            vm_qs = vm_qs.filter(caption__icontains=search)
        for m in vm_qs[:100]:
            # Try to get a village from the visit's villages
            v = m.visit.villages.first() if m.visit else None
            if village and village != "all" and (not v or v.slug != village):
                continue
            photos.append({
                "id": f"vm{m.pk}",
                "src": m.file.url,
                "thumb": m.file.url,
                "caption": m.caption,
                "village": v.name if v else "",
                "village_slug": v.slug if v else "",
                "category": "field_visit",
                "category_label": "Field Visit",
                "date": m.visit.date.strftime("%Y-%m-%d") if m.visit and m.visit.date else "",
                "lat": None,
                "lng": None,
                "tags": [],
                "width": 800,
                "height": 600,
                "is_featured": False,
            })

    return JsonResponse({"photos": photos, "total": len(photos)})


def gallery_map_data(request):
    """Photos with GPS coordinates for map pins."""
    qs = Photo.objects.filter(
        latitude__isnull=False, longitude__isnull=False
    ).select_related("village")[:500]
    points = []
    for p in qs:
        points.append({
            "id": p.pk,
            "lat": float(p.latitude),
            "lng": float(p.longitude),
            "thumb": p.thumbnail.url if p.thumbnail else p.image.url,
            "caption": p.caption[:100],
            "village": p.village.name if p.village else "",
        })
    return JsonResponse({"points": points})
