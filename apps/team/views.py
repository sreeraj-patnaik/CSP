from django.views.generic import TemplateView
from .models import TeamMember


class TeamView(TemplateView):
    template_name = "team/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mentor"] = TeamMember.objects.filter(role="mentor", is_active=True).first()
        ctx["leads"] = TeamMember.objects.filter(role="lead", is_active=True)
        ctx["members"] = TeamMember.objects.filter(role="member", is_active=True)
        ctx["volunteers"] = TeamMember.objects.filter(role="volunteer", is_active=True)
        return ctx
