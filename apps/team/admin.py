from django.contrib import admin
from django.utils.html import format_html
from .models import TeamMember


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("photo_preview", "name", "role", "designation", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("name", "designation", "roll_number")

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;">',
                obj.photo.url
            )
        return "—"
    photo_preview.short_description = "Photo"
