from django.contrib import admin
from django.utils.html import format_html
from .models import Village, VillageObservation


class VillageObservationInline(admin.TabularInline):
    model = VillageObservation
    extra = 1
    fields = ("title", "category", "content", "observation_date", "order")


@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ("name", "population", "survey_count_display", "internet_pct_display", "is_active", "order")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [VillageObservationInline]
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "slug", "description", "history", "is_active", "order"),
        }),
        ("Demographics", {
            "fields": ("population", "households", "area_sqkm", "primary_occupation"),
        }),
        ("Location", {
            "fields": ("latitude", "longitude", "nearby_landmarks"),
        }),
        ("Media", {
            "fields": ("hero_image", "thumbnail", "color_accent"),
        }),
        ("Field Notes", {
            "fields": ("internet_infrastructure", "challenges", "community_response"),
        }),
    )

    def survey_count_display(self, obj):
        return obj.survey_count
    survey_count_display.short_description = "Surveys"

    def internet_pct_display(self, obj):
        pct = obj.internet_usage_pct
        color = "#10B981" if pct >= 50 else "#F59E0B" if pct >= 25 else "#EF4444"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>', color, pct
        )
    internet_pct_display.short_description = "Internet Usage"


@admin.register(VillageObservation)
class VillageObservationAdmin(admin.ModelAdmin):
    list_display = ("village", "title", "category", "observation_date")
    list_filter = ("village", "category")
    search_fields = ("title", "content")
