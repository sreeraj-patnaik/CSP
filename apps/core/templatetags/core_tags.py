from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()


@register.filter
def jsonify(value):
    return mark_safe(json.dumps(value))


@register.filter
def percentage(value, total):
    try:
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def subtract(value, arg):
    return value - arg


@register.filter
def split(value, arg=","):
    return value.split(arg)


@register.simple_tag
def awareness_badge(level):
    colors = {
        "Very Low": "bg-red-500/20 text-red-400 border-red-500/30",
        "Low": "bg-orange-500/20 text-orange-400 border-orange-500/30",
        "Moderate": "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
        "High": "bg-green-500/20 text-green-400 border-green-500/30",
        "Very High": "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
    }
    css = colors.get(level, "bg-slate-500/20 text-slate-400 border-slate-500/30")
    return mark_safe(
        f'<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border {css}">{level}</span>'
    )


@register.simple_tag
def fraud_badge(value):
    colors = {
        "Yes": "bg-red-500/20 text-red-400 border-red-500/30",
        "No": "bg-green-500/20 text-green-400 border-green-500/30",
        "Not Sure": "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    }
    css = colors.get(value, "bg-slate-500/20 text-slate-400 border-slate-500/30")
    return mark_safe(
        f'<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border {css}">{value}</span>'
    )
