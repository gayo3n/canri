# views.py
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import MemberList, Member, Feedback, MemberParameter, MemberCareer
import json
from .forms import SearchForm


class IndexView(TemplateView):
    template_name = "index.html"

class MemberListView(TemplateView):
    template_name = "memberlist.html"



class MemberListMakeView(TemplateView):
    template_name = "memberList_make.html"
    def get(self, request, *args, **kwargs):
        form = SearchForm(request.GET) 
        return render(request, self.template_name, {'form': form})
    
    def get(self, request, *args, **kwargs):
        members = Member.objects.all()  # 初期状態で全メンバーを取得

        # 検索処理
        search_query = request.GET.get('query', '')  # 'query' というキーで取得
        print(f"Search query: {search_query}")  # 入力内容を確認

        if search_query:
            members = members.filter(name__icontains=search_query)
            print(f"Filtered members: {members}")  # フィルタリング結果を表示

        return render(request, self.template_name, {'members': members})


class MemberMakeView(TemplateView):
    template_name = "member_make.html"



class ManagementAccountView(TemplateView):
    template_name = "management_account.html"


#API関係

# メンバー情報を取得するAPI
@require_http_methods(["GET"])
def get_member_data(request, member_id):
    try:
        # 指定された member_id に一致するメンバー情報を取得
        member = Member.objects.get(member_id=member_id)
        carrer = MemberCareer.objects.get(member=member_id)
        memberparameter = MemberParameter.objects.get(member=member_id)
        # メンバー情報をJSONレスポンスとして返す
        member_data = {
            'member_id': member.member_id,
            'name': member.name,
            'birthdate': member.birthdate,

            'job_title': member.job_title,
            'career_id': carrer.career_id,
            'memo': member.memo,
            'mbti': member.mbti,  # ForeignKeyの場合、IDを返す
            'planning_presentation_power': memberparameter.planning_presentation_power,
            'teamwork': memberparameter.teamwork,
            'time_management_ability': memberparameter.time_management_ability,
            'problem_solving_ability': memberparameter.problem_solving_ability,
            'speciality_height': memberparameter.speciality_height,
        }
        return JsonResponse(member_data)
    
    except Member.DoesNotExist:
        return JsonResponse({"error": "指定されたメンバーが存在しません。"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# メンバーリストに対応したメンバー情報を取得するAPI
@require_http_methods(["GET"])
def get_members_by_member_list(request, member_list_id):
    try:
        # 指定された member_list_id に一致する MemberList を取得
        member_list = MemberList.objects.get(member_list_id=member_list_id)
        # MemberList の members フィールドを通じて関連するメンバー情報を取得
        members = member_list.member.all().values()
        
        # メンバー情報をJSONレスポンスで返す
        return JsonResponse(list(members), safe=False)
    
    except MemberList.DoesNotExist:
        return JsonResponse({"error": "指定されたメンバーリストが存在しません。"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

#チームを作成するAPI
@require_http_methods(["POST"])
def create_team_api(request):
    try:
        # リクエストボディからデータを取得
        data = json.loads(request.body)
        team_type = data.get('team_type')
        members = data.get('members')
        team_size = data.get('team_size')

        # team_type, members, team_size のバリデーションチェック
        if not team_type or not isinstance(members, list) or not team_size:
            return JsonResponse({"error": "無効なデータです"}, status=400)

        # チーム作成ロジックを呼び出し
        team = create_team(team_type, members, team_size)
        
        # チーム作成に失敗した場合のエラーハンドリング
        if isinstance(team, dict) and "error" in team:
            return JsonResponse(team, status=400)
        
        # 作成されたチームを JSON レスポンスとして返す
        return JsonResponse(team, safe=False)

    except json.JSONDecodeError:
        return JsonResponse({"error": "JSONデコードエラーが発生しました"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# チーム作成ロジック
# team_type = チームを作成する際の目的 | members = 作成に使用するメンバーのリスト | team_size = 作成するチームの人数 
# イベント用チーム = event | 研修用チーム = training | プロジェクト開発用チーム = project | アイデア発想チーム = idea_generation 
def create_team(team_type, members, team_size):
    # フィードバック情報を無条件で取得（削除フラグが False のもの）
    feedback_data = Feedback.objects.filter(deletion_flag=False)

    # メンバー同士の関係性を確認するための辞書を構築
    feedback_dict = {}
    for feedback in feedback_data:
        key = (feedback.member1_id, feedback.member2_id)
        feedback_dict[key] = feedback.priority_flag

    # チームの生成ロジック
    if team_type == 'event':
        sorted_members = sorted(members, key=lambda x: x['birthdate'])
        team = []
        left, right = 0, len(sorted_members) - 1
        while len(team) < team_size and left <= right:
            if len(team) % 2 == 0:
                member = sorted_members[left]
                left += 1
            else:
                member = sorted_members[right]
                right -= 1
            # フィードバック優先度を考慮
            if all(feedback_dict.get((member['member_id'], teammate['member_id']), False) for teammate in team):
                team.append(member)

    elif team_type == 'training':
        sorted_members = sorted(members, key=lambda x: x['level_of_expertise'], reverse=True)
        team = []
        for member in sorted_members:
            if len(team) < team_size:
                if all(feedback_dict.get((member['member_id'], teammate['member_id']), False) for teammate in team):
                    team.append(member)

    elif team_type == 'project':
        sorted_members = sorted(members, key=lambda x: (
            x['level_of_expertise'], 
            x['planning_presentation_power'], 
            x['teamwork'], 
            x['time_management_ability'], 
            x['problem_solving_ability']
        ), reverse=True)
        team = []
        for member in sorted_members:
            if len(team) < team_size:
                if all(feedback_dict.get((member['member_id'], teammate['member_id']), False) for teammate in team):
                    team.append(member)

    elif team_type == 'idea_generation':
        sorted_members = sorted(members, key=lambda x: x['planning_presentation_power'], reverse=True)
        team = []
        for member in sorted_members:
            if len(team) < team_size:
                if all(feedback_dict.get((member['member_id'], teammate['member_id']), False) for teammate in team):
                    team.append(member)
    else:
        return {"error": "無効なチームタイプです"}
    