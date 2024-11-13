from django import template
from canri_app.models import Team

register = template.Library()

@register.filter
def range_filter(start, end):
    return range(start, end)

@register.filter(name='get_team_by_id')
def get_team_by_id(team_id):
    try:
        team = Team.objects.get(team_id=team_id)
        team_data = {
            'team_id': team.team_id,
            'team_name': team.team_name,
            'count': team.count,
            'objective': team.objective,
            'memo': team.memo,
            'creation_date': team.creation_date,
            'update_date': team.update_date,
            'deletion_date': team.deletion_date,
        }
        return team_data
    except Team.DoesNotExist:
        return None