from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from .models import FieldVisit, VisitMedia
from apps.gallery.models import Photo


class VisitListView(ListView):
    model = FieldVisit
    template_name = "visits/list.html"
    context_object_name = "visits"
    queryset = (
        FieldVisit.objects
        .filter(is_published=True)
        .prefetch_related("villages", "team_members")
        .order_by("day_number")
    )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        visits = list(ctx["visits"])
        visit_ids = [v.pk for v in visits]

        # Build thumbnail map — VisitMedia first, then Photo fallback
        thumb_map = {}
        for vm in (
            VisitMedia.objects
            .filter(visit_id__in=visit_ids, media_type="photo")
            .order_by("visit_id", "order", "created_at")
        ):
            if vm.visit_id not in thumb_map and vm.file:
                thumb_map[vm.visit_id] = vm.file.url

        for p in (
            Photo.objects
            .filter(visit_id__in=visit_ids)
            .order_by("visit_id", "-is_featured", "order", "-created_at")
        ):
            if p.visit_id not in thumb_map:
                url = (p.thumbnail.url if p.thumbnail else
                       p.image.url if p.image else None)
                if url:
                    thumb_map[p.visit_id] = url

        for visit in visits:
            visit.thumbnail_url = thumb_map.get(visit.pk)

        ctx["visits"] = visits
        ctx["village_count"] = (
            FieldVisit.objects.filter(is_published=True)
            .values("villages").distinct().count()
        )
        return ctx


class VisitDetailView(DetailView):
    model = FieldVisit
    template_name = "visits/detail.html"
    context_object_name = "visit"

    def get_object(self):
        return get_object_or_404(FieldVisit, day_number=self.kwargs["day"], is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        visit = self.object
        ctx["photos"] = Photo.objects.filter(visit=visit).select_related("village").order_by("order", "-created_at")
        ctx["vm_photos"] = visit.media.filter(media_type="photo").order_by("order")
        ctx["total_photo_count"] = ctx["photos"].count() + ctx["vm_photos"].count()
        ctx["videos"] = visit.media.filter(media_type="video").order_by("order")
        ctx["documents"] = visit.media.filter(media_type="document").order_by("order")
        ctx["prev_visit"] = FieldVisit.objects.filter(
            day_number__lt=visit.day_number, is_published=True
        ).order_by("-day_number").first()
        ctx["next_visit"] = FieldVisit.objects.filter(
            day_number__gt=visit.day_number, is_published=True
        ).order_by("day_number").first()
        ctx["all_visits"] = FieldVisit.objects.filter(is_published=True).values(
            "day_number", "title", "date"
        )
        # Hero thumbnail for the detail page header
        hero = (
            visit.media.filter(media_type="photo").order_by("order").first()
            or Photo.objects.filter(visit=visit).order_by("-is_featured", "order").first()
        )
        ctx["hero_photo_url"] = (
            hero.file.url if hasattr(hero, "file") and hero.file
            else hero.image.url if hero and hasattr(hero, "image") and hero.image
            else None
        )
        return ctx
