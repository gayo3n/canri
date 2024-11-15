from django import template
from canri_app.models import Team

register = template.Library()

@register.filter
def range_filter(start, end):
    return range(start, end)

