from django import template
from canri_app.models import MemberList

register = template.Library()

# リストからインデックスでアイテムを取得するフィルタ
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


@register.filter
def dict_key(dict_obj, key):
    return dict_obj.get(key, '')