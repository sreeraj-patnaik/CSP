from .models import SiteSettings


def site_context(request):
    settings_obj = SiteSettings.get()
    return {
        "site_settings": settings_obj,
        "project_name": settings_obj.project_name,
        "mentor_name": settings_obj.mentor_name,
    }
