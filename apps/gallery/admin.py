from django.contrib import admin
from django.utils.html import format_html
from .models import Photo


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("thumbnail_preview", "caption_short", "village", "category", "date_taken", "is_featured")
    list_editable = ("is_featured",)
    list_filter = ("village", "visit", "category", "is_featured")
    search_fields = ("caption", "tags")
    readonly_fields = ("width", "height", "file_size", "exif_data", "created_at")

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:60px;height:45px;object-fit:cover;border-radius:4px;">',
                obj.image.url
            )
        return "—"
    thumbnail_preview.short_description = "Preview"

    def caption_short(self, obj):
        return obj.caption[:80] if obj.caption else "—"
    caption_short.short_description = "Caption"
