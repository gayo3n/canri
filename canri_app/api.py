from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import MemberList, Member, Feedback, MemberParameter, MemberCareer, JobTitleInformation, MemberHoldingQualification, Team, ProjectAffiliationTeam, Project, Category, TeamMember
import json
from django.utils import timezone

#API関係

# 特定のメンバー情報を取得するAPI
@require_http_methods(["GET"])
def get_member_data(request, member_id):
    try:
        # 指定された member_id に一致するメンバー情報を取得
        member = Member.objects.get(member_id=member_id)
        carrer = MemberCareer.objects.get(member=member_id)
        memberparameter = MemberParameter.objects.get(member=member_id)
        try:
            memberjob = JobTitleInformation.objects.get(job_title=member.job_title)
        except JobTitleInformation.DoesNotExist:
            memberjob = None
        # 同じメンバーIDを持つ資格を3件まで取得
        memberqualification = MemberHoldingQualification.objects.filter(member=member_id)[:3]
        # メンバー情報を辞書として返す
        member_data = {
            'member_id': member.member_id,#メンバーID
            'name': member.name,#名前
            'birthdate': member.birthdate,#生年月日
            'career_id': carrer.career.career_id,#職歴ID
            'career_name': carrer.career.career,#職歴名
            'job_id_title_id': memberjob.job_title_id if memberjob else None,#役職ID
            'job_title': member.job_title,#役職名
            'mbti': {
                'mbti_id': member.mbti.mbti_id,
                'mbti_name': member.mbti.mbti_name,
                'planning_presentation_power': member.mbti.planning_presentation_power,
                'teamwork': member.mbti.teamwork,
                'time_management_ability': member.mbti.time_management_ability,
                'problem_solving_ability': member.mbti.problem_solving_ability
            },#MBTI
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

        return JsonResponse({'member_data': member_data})
    
    except Member.DoesNotExist:
        return JsonResponse({'error': 'Member not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# メンバーリストに対応したメンバー情報を取得するAPI
@require_http_methods(["GET"])
def get_members_by_member_list(request, category_id):
    try:
        # 指定された category_id に一致する MemberList を取得
        member_lists = MemberList.objects.filter(category=category_id, deletion_flag=False)
        members = Member.objects.filter(memberlist__in=member_lists, deletion_flag=False).distinct()

        # メンバー情報を辞書形式で返す
        return JsonResponse({'members': list(members.values())})
    
    except MemberList.DoesNotExist:
        return JsonResponse({'error': 'MemberList not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

#チームを作成するAPI
@require_http_methods(["POST"])
def create_team_api(request):
    try:
        # リクエストボディからデータを取得
        data = json.loads(request.body)
        team_type = data.get('team_type')
        member_ids = data.get('members')
        team_size = data.get('team_size')

        # team_type, members, team_size のバリデーションチェック
        if not team_type or not isinstance(member_ids, list) or not team_size:
            return JsonResponse({"error": "無効なデータです"}, status=400)

        # メンバーIDから各メンバーの情報を取得
        members = []
        for member_id in member_ids:
            try:
                member_id = int(member_id)  # member_id を整数に変換
                member = Member.objects.get(member_id=member_id)
                member_parameter = MemberParameter.objects.get(member=member)
                members.append({
                    'member_id': member.member_id,
                    'name': member.name,
                    'birthdate': member.birthdate,
                    'planning_presentation_power': member_parameter.planning_presentation_power,
                    'teamwork': member_parameter.teamwork,
                    'time_management_ability': member_parameter.time_management_ability,
                    'problem_solving_ability': member_parameter.problem_solving_ability,
                    'speciality_height': member_parameter.speciality_height
                })
            except Member.DoesNotExist:
                return JsonResponse({'error': f'Member with ID {member_id} not found'}, status=404)
            except MemberParameter.DoesNotExist:
                return JsonResponse({'error': f'MemberParameter for member ID {member_id} not found'}, status=404)

        # チーム作成ロジックを呼び出し
        team = create_team(team_type, members, team_size)
        
        # チーム作成に失敗した場合のエラーハンドリング
        if isinstance(team, dict) and "error" in team:
            return JsonResponse(team, status=400)
        
        # 作成されたチームを辞書形式として返す
        return JsonResponse({'team': team})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# チーム作成ロジック
# team_type = チームを作成する際の目的 | members = 作成に使用するメンバーのリスト | team_size = 作成するチームの人数 
# イベント用チーム = event
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
        while len(team) < int(team_size) and left <= right:
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
        sorted_members = sorted(members, key=lambda x: x['speciality_height'], reverse=True)
        team = []
        for member in sorted_members:
            if len(team) < int(team_size):
                if all(feedback_dict.get((member['member_id'], teammate['member_id']), False) for teammate in team):
                    team.append(member)

    elif team_type == 'project':
        sorted_members = sorted(members, key=lambda x: (
            x['speciality_height'], 
            x['planning_presentation_power'], 
            x['teamwork'], 
            x['time_management_ability'], 
            x['problem_solving_ability']
        ), reverse=True)
        team = []
        for member in sorted_members:
            if len(team) < int(team_size):
                if all(feedback_dict.get((member['member_id'], teammate['member_id']), False) for teammate in team):
                    team.append(member)

    elif team_type == 'idea_generation':
        sorted_members = sorted(members, key=lambda x: x['planning_presentation_power'], reverse=True)
        team = []
        for member in sorted_members:
            if len(team) < int(team_size):
                if all(feedback_dict.get((member['member_id'], teammate['member_id']), False) for teammate in team):
                    team.append(member)
    else:
        return {"error": "無効なチームタイプです"}

    return team

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
        return JsonResponse({'teams': team_data})

    except ProjectAffiliationTeam.DoesNotExist:
        return JsonResponse({'error': 'ProjectAffiliationTeam not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

#チームに所属するメンバーを取得するAPI
@require_http_methods(["GET"])
def get_team_members(request, team_id):
    try:
        # チームIDに関連するメンバーを取得（deletion_flagがFalseのものに限定）
        team_members = TeamMember.objects.filter(team=team_id, deletion_flag=False)
        # メンバー情報をリストに格納
        member_data = []
        for team_member in team_members:
            member = team_member.member
            memberparameter = MemberParameter.objects.get(member=member)
            carrer = MemberCareer.objects.get(member=member)
            try:
                memberjob = JobTitleInformation.objects.get(job_title=member.job_title)
            except JobTitleInformation.DoesNotExist:
                memberjob = None
            member_data.append({
                'member_id': member.member_id,#メンバーID
            'name': member.name,#名前
            'birthdate': member.birthdate,#生年月日
            'career_id': carrer.career.career_id,#職歴ID
            'career_name': carrer.career.career,#職歴名
            'job_id_title_id': memberjob.job_title_id if memberjob else None,#役職ID
            'job_title': member.job_title,#役職名
            'mbti': {
                'mbti_id': member.mbti.mbti_id,
                'mbti_name': member.mbti.mbti_name,
                'planning_presentation_power': member.mbti.planning_presentation_power,
                'teamwork': member.mbti.teamwork,
                'time_management_ability': member.mbti.time_management_ability,
                'problem_solving_ability': member.mbti.problem_solving_ability
            },#MBTI
            'planning_presentation_power': memberparameter.planning_presentation_power,#企画・プレゼン力
            'teamwork': memberparameter.teamwork,#チームワーク
            'time_management_ability': memberparameter.time_management_ability,#時間管理能力
            'problem_solving_ability': memberparameter.problem_solving_ability,#問題解決能力
            'speciality_height': memberparameter.speciality_height,#専門性の高さ
            'memo': member.memo,#メンバー個人メモ
            })
        
        # 辞書形式でメンバー情報を返す
        return JsonResponse({'members': member_data})

    except TeamMember.DoesNotExist:
        return JsonResponse({'error': 'TeamMember not found'}, status=404)
    except MemberParameter.DoesNotExist:
        return JsonResponse({'error': 'MemberParameter not found'}, status=404)
    except Exception as e:
        print(f"Error: {str(e)}")  # エラーメッセージを出力
        return JsonResponse({'error': str(e)}, status=500)

# チーム情報を取得するAPI
@require_http_methods(["GET"])
def get_team_data(request, team_id):
    try:
        # 指定されたteam_id に一致するチーム情報を取得
        team = Team.objects.get(team_id=team_id)
        
        # チーム情報を辞書として返す
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
        
        return JsonResponse({'team': team_data})
    
    except Team.DoesNotExist:
        return JsonResponse({'error': 'Team not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# 新規チームを保存するAPI
@require_http_methods(["POST"])
def save_team_api(request):
    try:
        # リクエストボディからデータを取得
        data = json.loads(request.body)
        team_name = data.get('team_name')
        team_type = data.get('team_type')
        team_members = data.get('team')

        # team_name, team_type, team_members のバリデーションチェック
        if not team_name or not team_type or not isinstance(team_members, list):
            return JsonResponse({"error": "無効なデータです"}, status=400)

        # チームを作成
        team = Team.objects.create(
            team_name=team_name,
            count=len(team_members),
            objective=team_type,
            creation_date=timezone.now()
        )

        # チームメンバーを追加
        for member_id in team_members:
            member = Member.objects.get(member_id=member_id)
            TeamMember.objects.create(
                team=team,
                member=member,
                creation_date=timezone.now(),
                update_date=timezone.now()
            )

        return JsonResponse({'team_id': team.team_id})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Member.DoesNotExist:
        return JsonResponse({'error': 'Member not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# プロジェクトを保存するAPI
@require_http_methods(["POST"])
def save_project_api(request):
    try:
        # リクエストボディからデータを取得
        data = json.loads(request.body)
        project_name = data.get('project_name')
        project_description = data.get('project_description')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        teams = data.get('teams')

        # バリデーションチェック
        if not project_name or not project_description or not start_date or not end_date or not isinstance(teams, list):
            return JsonResponse({"error": "無効なデータです"}, status=400)

        # プロジェクトを作成
        project = Project.objects.create(
            project_name=project_name,
            project_detail=project_description,
            project_start_date=start_date,
            project_end_date=end_date,
            creation_date=timezone.now()
        )

        # チームをプロジェクトに関連付け
        for team_id in teams:
            team = Team.objects.get(team_id=team_id)
            ProjectAffiliationTeam.objects.create(
                team=team,
                project=project,
                creation_date=timezone.now()
            )

        return JsonResponse({'project_id': project.project_id})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Team.DoesNotExist:
        return JsonResponse({'error': 'Team not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# チーム削除API
@require_http_methods(["POST"])
def delete_team_api(request):
    try:
        data = json.loads(request.body)
        team_id = data.get('team_id')
        teams = data.get('teams')
        project_name = data.get('project_name')
        project_description = data.get('project_description')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        try:
            # チームとチームメンバーの削除フラグを1に設定
            team = Team.objects.get(team_id=team_id)
            team.deletion_flag = 1
            team.save()

            TeamMember.objects.filter(team=team).update(deletion_flag=1)

            # teamsからチームIDを削除
            teams = [t for t in teams if t != int(team_id)]
        except Team.DoesNotExist:
            return JsonResponse({'error': 'Team not found'}, status=404)

        # 入力された情報をリスト化
        project_data = {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date
        }

        return JsonResponse({'project': project_data, 'teams': teams})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

