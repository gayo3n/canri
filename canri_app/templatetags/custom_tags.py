from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def get_base_template(context):
    user = context['request'].user
    if user.is_superuser:
        return 'base2.html'
    else:
        return 'base.html'