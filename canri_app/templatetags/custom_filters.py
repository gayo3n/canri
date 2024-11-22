from django import template
from canri_app.models import Team

register = template.Library()

@register.filter
def range_filter(start, end):
    return range(start, end)

# メンバーリスト作成
@register.filter
def get_item(list, index):
    try:
        return list[index]
    except IndexError:
        return None