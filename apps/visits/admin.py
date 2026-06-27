from django.contrib import admin
from .models import FieldVisit, VisitMedia
from apps.gallery.models import Photo


class VisitMediaInline(admin.TabularInline):
    model = VisitMedia
    extra = 1
    fields = ("media_type", "file", "caption", "order")
    verbose_name = "Photo / Video / Document"
    verbose_name_plural = "Media (Photos, Videos, Documents)"


class VisitPhotoInline(admin.TabularInline):
    model = Photo
    fk_name = "visit"
    extra = 1
    fields = ("image", "caption", "village", "category", "is_featured", "order")
    verbose_name = "Photo"
    verbose_name_plural = "Photos (also appear in Gallery)"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("village")


@admin.register(FieldVisit)
class FieldVisitAdmin(admin.ModelAdmin):
    list_display = ("day_number", "title", "date", "village_list", "attendance", "surveys_collected", "is_published")
    list_editable = ("is_published",)
    list_filter = ("is_published", "villages")
    search_fields = ("title", "summary", "observations")
    filter_horizontal = ("villages", "team_members")
    inlines = [VisitPhotoInline, VisitMediaInline]
    fieldsets = (
        ("Visit Info", {
            "fields": ("day_number", "title", "date", "is_published"),
        }),
        ("Villages & Team", {
            "fields": ("villages", "team_members"),
            "description": "Select all villages visited and all team members who attended.",
        }),
        ("Content", {
            "fields": ("summary", "objectives", "activities"),
        }),
        ("Statistics", {
            "fields": ("attendance", "surveys_collected"),
        }),
        ("Field Notes", {
            "fields": ("observations", "problems_faced", "solutions", "lessons_learned", "impact"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Villages")
    def village_list(self, obj):
        return ", ".join(v.name for v in obj.villages.all()) or "—"


@admin.register(VisitMedia)
class VisitMediaAdmin(admin.ModelAdmin):
    list_display = ("visit", "media_type", "caption", "order")
    list_filter = ("media_type",)
