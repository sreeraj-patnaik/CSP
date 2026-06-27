"""Root URL configuration."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "CSP Cyber Awareness — Admin"
admin.site.site_title = "CSP Admin"
admin.site.index_title = "Portal Administration"

urlpatterns = [
    path("admin/", admin.site.urls),

    # Core / Landing
    path("", include("apps.core.urls", namespace="core")),

    # Feature apps
    path("villages/", include("apps.villages.urls", namespace="villages")),
    path("visits/", include("apps.visits.urls", namespace="visits")),
    path("survey/", include("apps.surveys.urls", namespace="surveys")),
    path("gallery/", include("apps.gallery.urls", namespace="gallery")),
    path("analytics/", include("apps.analytics.urls", namespace="analytics")),
    path("reports/", include("apps.reports.urls", namespace="reports")),
    path("ai/", include("apps.ai_assistant.urls", namespace="ai")),
    path("team/", include("apps.team.urls", namespace="team")),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),

    # API
    path("api/villages/", include("apps.villages.api_urls", namespace="api-villages")),
    path("api/surveys/", include("apps.surveys.api_urls", namespace="api-surveys")),
    path("api/analytics/", include("apps.analytics.api_urls", namespace="api-analytics")),
    path("api/gallery/", include("apps.gallery.api_urls", namespace="api-gallery")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
