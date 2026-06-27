from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Project Information", {
            "fields": ("project_name", "project_topic", "mentor_name", "college_name", "academic_year"),
        }),
        ("Appearance", {
            "fields": ("logo", "hero_video", "hero_tagline"),
        }),
        ("Feature Flags", {
            "fields": ("show_ai_assistant", "survey_open", "maintenance_mode"),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
