from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import MemberList, Member, Feedback, MemberParameter, MemberCareer, JobTitleInformation, MemberHoldingQualification, Team, ProjectAffiliationTeam, TeamMember
import json

#API関係

# 特定のメンバー情報を取得するAPI
@require_http_methods(["GET"])
def get_member_data(request, member_id):
    try:
        # 指定された member_id に一致するメンバー情報を取得
        member = Member.objects.get(member_id=member_id)
        carrer = MemberCareer.objects.get(member=member_id)
        memberparameter = MemberParameter.objects.get(member=member_id)
        memberjob = JobTitleInformation.objects.get(job_title=member.job_title)
        # 同じメンバーIDを持つ資格を3件まで取得
        memberqualification = MemberHoldingQualification.objects.filter(member=member_id)[:3]
        # メンバー情報を辞書として返す
        member_data = {
            'member_id': member.member_id,#メンバーID
            'name': member.name,#名前
            'birthdate': member.birthdate,#生年月日
            'career_id': carrer.career,#職歴ID
            'job_id_title_id': memberjob.job_title_id,#役職ID
            'job_title': member.job_title,#役職名
            'mbti': member.mbti,#MBTI
            'planning_presentation_power': memberparameter.planning_presentation_power,#企画・プレゼン力
            'teamwork': memberparameter.teamwork,#チームワーク
            'time_management_ability': memberparameter.time_management_ability,#時間管理能力
            'problem_solving_ability': memberparameter.problem_solving_ability,#問題解決能力
            'speciality_height': memberparameter.speciality_height,#専門性の高さ
            'memo': member.memo,#メンバー個人メモ
        }

        # 資格情報をリストに追加して辞書に格納(最大3つ)
        qualifications_data = []
        for i, qualification in enumerate(memberqualification):
            qualifications_data.append({
                f'qualification_id{i+1}': qualification.holding_qualification_id,
                f'qualification_name{i+1}': qualification.qualification.qualification_name,  # 資格の名前（例: 'qualification_name' フィールドを想定）
            })

        # メンバー情報に資格情報を追加
        member_data['qualifications'] = qualifications_data

        return render(request, 'template_name.html', {'member_data': member_data})
    
    except Member.DoesNotExist:
        return render(request, 'template_name.html', {'error': 'error'})
    except Exception as e:
        return render(request, 'template_name.html', {'error': 'error'})

# メンバーリストに対応したメンバー情報を取得するAPI
@require_http_methods(["GET"])
def get_members_by_member_list(request, member_list_id):
    try:
        # 指定された member_list_id に一致する MemberList を取得
        member_list = MemberList.objects.get(member_list_id=member_list_id)
        # MemberList の members フィールドを通じて関連するメンバー情報を取得
        members = member_list.member.all().values()
        
        # メンバー情報を辞書形式で返す
        return render(request, 'template_name.html', {'members': list(members)})
    
    except MemberList.DoesNotExist:
        return render(request, 'template_name.html', {'error': 'error404'})
    except Exception as e:
        return render(request, 'template_name.html', {'error': 'error500'})

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
            return render(request, 'template_name.html', {"error": "無効なデータです"}, status=400)

        # チーム作成ロジックを呼び出し
        team = create_team(team_type, members, team_size)
        
        # チーム作成に失敗した場合のエラーハンドリング
        if isinstance(team, dict) and "error" in team:
            return render(request, 'template_name.html', team, status=400)
        
        # 作成されたチームを辞書形式として返す
        return render(request, 'template_name.html', {'team': team})

    except json.JSONDecodeError:
        return render(request, 'template_name.html', {'error': 'error400'})
    except Exception as e:
        return render(request, 'template_name.html', {'error': 'error500'})

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

#プロジェクトチームの一覧を取得するAPI
@require_http_methods(["GET"])
def get_teams_by_project(request, project_id):
    try:
        # ProjectAffiliationTeamで指定されたプロジェクトIDに関連するチームIDを取得
        affiliation_teams = ProjectAffiliationTeam.objects.filter(
            project=project_id, deletion_flag=False
        )

        # 関連するチーム情報を取得
        team_data = []
        for affiliation in affiliation_teams:
            team = affiliation.team
            team_data.append({
                'team_id': team.team_id,
                'team_name': team.team_name,
                'count': team.count,
                'objective': team.objective,
                'memo': team.memo,
                'creation_date': team.creation_date,
                'update_date': team.update_date,
                'deletion_date': team.deletion_date,
            })

        # 辞書形式でチーム情報を返す
        return render(request, 'template_name.html', {'teams': team_data})

    except ProjectAffiliationTeam.DoesNotExist:
        return render(request, 'template_name.html', {'error': 'error404'})
    except Exception as e:
        return render(request, 'template_name.html', {'error': 'error500'})

#チームに所属するメンバーを取得するAPI
@require_http_methods(["GET"])
def get_team_members(request, team_id):
    try:
        # チームIDに関連するメンバーを取得（deletion_flagがFalseのものに限定）
        team_members = TeamMember.objects.filter(team=team_id, deletion_flag=False)
        # メンバー情報をリストに格納
        member_data = []
        for team_member in team_members:
            member = team_member.member_id
            memberparameter = MemberParameter.objects.get(member=member)
            member_data.append({
                'team_member_id': team_member.team_member_id,
                'member_id': member.member_id,
                'name': member.name,
                'birthdate': member.birthdate,
                'job_title': member.job_title,
                'mbti': member.mbti,
                'creation_date': team_member.creation_date,
                'update_date': team_member.update_date,
                'planning_presentation_power': memberparameter.planning_presentation_power,#企画・プレゼン力
                'teamwork': memberparameter.teamwork,#チームワーク
                'time_management_ability': memberparameter.time_management_ability,#時間管理能力
                'problem_solving_ability': memberparameter.problem_solving_ability,#問題解決能力
                'speciality_height': memberparameter.speciality_height,#専門性の高さ
            })

        # 辞書形式でメンバー情報を返す
        return render(request, 'template_name.html', {'members': member_data})

    except TeamMember.DoesNotExist:
        return render(request, 'template_name.html', {'error': 'error404'})
    except Exception as e:
        return render(request, 'template_name.html', {'error': 'error500'})