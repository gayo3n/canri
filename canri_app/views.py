# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import *
from .models import MemberList, Member, Feedback, MemberParameter, MemberCareer, JobTitleInformation, MemberHoldingQualification, Project,CareerInformation,MBTI,Credentials,Category
from django.utils import timezone
import json
from .forms import SearchForm
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect
from .api import create_team_api, save_team_api, save_project_api, get_member_data
from django.urls import reverse



# -----システムメニュー-----
class IndexView(TemplateView):
    template_name = "index.html"

# -----------ログインでセッション未設定だと思われるため、まだ機能してません--百----------

    def my_view(request):
        if request.user.is_authenticated:
            # ユーザーはログインしています
            template_name = "index.html"
            user_name = models.User.name
            return render(request, template_name, {"name" : user_name})
        else:
            # ユーザーはログインしていません
            return redirect('accounts:login/')


# -----メンバーリスト一覧-----
class MemberListView(TemplateView):
    template_name = "memberlist.html"

class NewProjectView(TemplateView):
    template_name = "create_new_project.html"



# -----メンバーリスト作成-----
class MemberListMakeView(TemplateView):
    template_name = "memberList_make.html"
    
    memberID_list = []

    def get(self, request, *args, **kwargs):
        form = SearchForm(request.GET)
        members = Member.objects.all()

        context = {
            'form': form,
            'members': members,
            'memberID_list': self.memberID_list
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        members = Member.objects.all()

        # 検索処理
        search_query = request.POST.get('query', '')
        if search_query:
            members = members.filter(name__icontains=search_query)
        
        # 複数のmember_id をリクエストから取得
        member_ids = request.POST.getlist('member_id')

        # member_idが複数選ばれている場合
        if member_ids:
            for member_id in member_ids:
                if member_id.isdigit():  # 数値チェッ��
                    try:
                        # メンバーを取得
                        member = Member.objects.get(member_id=int(member_id))
                        if member_id not in self.memberID_list:
                            self.memberID_list.append(member_id)
                    except Member.DoesNotExist:
                        pass  # メンバーが存在しない場合は無視

        # member_id が追加されていれば、そのメンバー情報を取得
        members_in_list = Member.objects.filter(member_id__in=self.memberID_list)

        context = {
            'members': members,
            'memberID_list': self.memberID_list,
            'members_in_list': members_in_list  # 追加されたメンバーを表示するための変数
        }

        return render(request, self.template_name, context)

class MemberListMakeCompleteView(TemplateView):
    template_name = "memberList_make_complete.html"

# メンバー作成
class MemberMakeView(TemplateView):
    template_name = "member_make.html"
    def get(self, request, *args, **kwargs):
        mbti = MBTI.objects.all()  # 複数のフィールドを取得
        job_title = JobTitleInformation.objects.all()
        credentials = Credentials.objects.all()
        careerinformation = CareerInformation.objects.all()
        context = {
        'mbti': mbti,
        'job_title': job_title,
        'credentials': credentials,
        'careerinformation': careerinformation,
    }
        return render(request, 'member_make.html', context)

class MemberMakeCompleteView(TemplateView):
    template_name = "member_make_complete.html"

class MemberMakeDeleteView(TemplateView):
    template_name = "member_make_delete.html"

class MemberListDeleteView(TemplateView):
    template_name = "memberlist_delete.html"

class MemberListDeleteOkView(TemplateView):
    template_name = "memberlist_delete_complete.html"

class MemberMakeDeleteOkView(TemplateView):
    template_name = "member_make_delete_complete.html"

#新規プロジェクト作成
class NewProjectView(TemplateView):
    template_name = "new_project.html"

#新規プロジェクト編集
class NewProjectEditView(TemplateView):
    template_name = "new_project_edit.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # 入力された情報をリスト化
        project_data = {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date
        }

        # 空のチームリストを追加
        teams = []

        # 入力された情��を保持した状態でnew_project_edit.htmlに遷移
        return render(request, self.template_name, {'project': project_data, 'teams': teams})

#新規プロジェクト編集に戻る
class NewProjectEdit2View(TemplateView):
    template_name = "new_project_edit.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')

        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        # 入力された情報をリスト化
        project_data = {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date
        }

        # 入力された情報を保持した状態でnew_project_edit.htmlに遷移
        return render(request, self.template_name, {'project': project_data, 'teams': teams})

#チーム追加１
class CreateTeamView(TemplateView):
    template_name = "create_team.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')

        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        # 入力された情報を保持した状態でcreate_team.htmlに遷移
        return render(request, self.template_name, {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date,
            'teams': teams
        })

#チーム追加2
class CreateTeam2View(TemplateView):
    template_name = "create_team2.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')
        team_size = request.POST.get('team_size')
        team_type = request.POST.get('team_type')
        auto_generate = request.POST.get('auto_generate')
        categories = Category.objects.filter(deletion_flag=False)

        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        if auto_generate:
            # 入力された情報を保持した状態でcreate_team2.htmlに遷移
            return render(request, self.template_name, {
                'project_name': project_name,
                'project_description': project_description,
                'start_date': start_date,
                'end_date': end_date,
                'teams': teams,
                'team_size': team_size,
                'team_type': team_type,
                'categories': categories,
            })
        else:
            # 入力された情報を保持した状態でcreate_team3.htmlに遷移
            return render(request, 'create_team3.html', {
                'project_name': project_name,
                'project_description': project_description,
                'start_date': start_date,
                'end_date': end_date,
                'teams': teams,
                'team_type': team_type,
                'categories': categories,
            })

#チーム追加2に戻る
class CreateTeam2BackView(TemplateView):
    template_name = "create_team2.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')
        team_size = request.POST.get('team_size')
        team_type = request.POST.get('team_type')
        categories = Category.objects.filter(deletion_flag=False)

        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        # 入力された情報を保持した状態でcreate_team.htmlに遷移
        return render(request, self.template_name, {
                'project_name': project_name,
                'project_description': project_description,
                'start_date': start_date,
                'end_date': end_date,
                'teams': teams,
                'team_size': team_size,
                'team_type': team_type,
                'categories': categories,
            })

#チーム追加3
class CreateTeam3View(TemplateView):
    template_name = "create_team3.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')
        team_size = request.POST.get('team_size')
        team_type = request.POST.get('team_type')
        categories = Category.objects.filter(deletion_flag=False)
        selected_members = json.loads(request.POST.get('selected_members'))

        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        # チームを編成するためのデータを作成
        data = {
            'team_type': team_type,
            'members': selected_members,
            'team_size': team_size
        }

        # create_team_api を呼び出し���チームを編成
        request._body = json.dumps(data).encode('utf-8')
        response = create_team_api(request)
        response_data = json.loads(response.content)

        if response.status_code == 200:
            team = response_data['team']
            print("チームが作成されました:", team)  # メンバー情報をターミナルに表示
        else:
            team = None
            print("チームの作成に失敗しました")  # エラーメッセージをターミナルに表示

        # 入力された情報を保持した状態でcreate_team3.htmlに遷移
        return render(request, self.template_name, {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date,
            'teams': teams,
            'team_size': team_size,
            'team_type': team_type,
            'categories': categories,
            'selected_members': selected_members,
            'team': team
        })

#チーム保存
class SaveTeamView(TemplateView):
    template_name = "new_project_edit.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')
        team_name = request.POST.get('team_name')
        team_type = request.POST.get('team_type')
        team = request.POST.get('team')

        # デバッグ用にリクエストボディを表示
        print("リクエストボディ:", request.body)

        try:
            teams = json.loads(teams)
            team = json.loads(team)
        except json.JSONDecodeError as e:
            print("JSONDecodeError:", e)
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        # チームを保存するためのデータを作成
        data = {
            'team_name': team_name,
            'team_type': team_type,
            'team': team
        }

        # save_team_api を呼び出してチームを保存
        request._body = json.dumps(data).encode('utf-8')
        response = save_team_api(request)
        response_data = json.loads(response.content)

        if response.status_code == 200:
            team_id = response_data['team_id']
            if isinstance(teams, list):
                teams.append(team_id)
            else:
                teams = [team_id]
            print("チームが保存されました:", team_id)  # チームIDをターミナルに表示
        else:
            print(response_data)
            print("チームの保存に失敗しました")  # エラーメッセージをターミナルに表示

        # 入力された情報をリスト化
        project_data = {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date
        }

        # 入力された情報を保持した状態でnew_project_edit.htmlに遷移
        return render(request, self.template_name, {'project': project_data, 'teams': teams})

#新規プロジェクト保存
class SaveNewProjectView(TemplateView):
    template_name = "save_new_project.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description') 
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')

        # プロジェクトを保存するためのデータを作成
        data = {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date,
            'teams': json.loads(teams)
        }

        # save_project_api を呼び出してプロジェクトを保存
        request._body = json.dumps(data).encode('utf-8')
        response = save_project_api(request)
        response_data = json.loads(response.content)

        if response.status_code == 200:
            project_id = response_data['project_id']
            print("プロジェクト��保存されました:", project_id)  # プロジェクトIDをターミナルに表示
        else:
            print(response_data)
            print("プロジェクトの保存に失敗しました")  # エラーメッセージをターミナルに表示

        # 入力された情報を保持した状態でsave_new_project.htmlに遷移
        return render(request, self.template_name, {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date,
            'teams': teams
        })

#チーム編集
class TeamEditView(TemplateView):
    template_name = "team_edit.html"

    def get(self, request, *args, **kwargs):
        team_id = kwargs.get('team_id')
        team = Team.objects.get(team_id=team_id)
        members = TeamMember.objects.filter(team=team)
        categories = Category.objects.filter(deletion_flag=False)

        project_name = request.GET.get('project_name')
        project_description = request.GET.get('project_description')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        teams = request.GET.get('teams')
        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        context = {
            'team': team,
            'members': members,
            'categories': categories,
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date,
            'teams': teams,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        team_id = kwargs.get('team_id')
        team = Team.objects.get(team_id=team_id)
        team_name = request.POST.get('team_name')
        team_memo = request.POST.get('team_memo')
        team_members = request.POST.get('team')
        if not team_members:
            team_members = []
        else:
            team_members = json.loads(team_members)
        print("team_memo:", team_memo)

        team.team_name = team_name
        team.memo = team_memo
        team.save()

        TeamMember.objects.filter(team=team).delete()
        for member_id in team_members:
            member = Member.objects.get(member_id=member_id)
            TeamMember.objects.create(
                team=team,
                member=member,
                creation_date=timezone.now(),
                update_date=timezone.now()
            )

        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')

        return HttpResponseRedirect(f"{reverse('canri_app:team_edit_complete')}?project_name={project_name}&project_description={project_description}&start_date={start_date}&end_date={end_date}&teams={teams}&team_members={team_members}")

#チーム編集完了
class TeamEditCompleteView(TemplateView):
    template_name = "new_project_edit.html"

    def get(self, request, *args, **kwargs):
        project_name = request.GET.get('project_name')
        project_description = request.GET.get('project_description')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        teams = request.GET.get('teams')

        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        project_data = {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date
        }

        return render(request, self.template_name, {'project': project_data, 'teams': teams})

#チーム削除
class TeamDeleteView(TemplateView):
    template_name = "new_project_edit.html"

    def post(self, request, *args, **kwargs):
        team_id = request.POST.get('team_id')
        teams = request.POST.get('teams')
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        try:
            # チームとチームメンバーの削除フラグを1に設定
            team = Team.objects.get(team_id=team_id)
            team.deletion_flag = True
            team.save()

            TeamMember.objects.filter(team=team).update(deletion_flag=True)

            # teamsからチームIDを削除
            teams = [t for t in teams if t != int(team_id)]
        except Team.DoesNotExist:
            return HttpResponseNotFound("Team not found")

        # 入力された情報をリスト化
        project_data = {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date
        }

        # 入力された情報を保持した状態でnew_project_edit.htmlに遷移
        return render(request, self.template_name, {'project': project_data, 'teams': teams})

#チームメンバー編集
class TeamMemberEditView(TemplateView):
    template_name = "team_edit.html"

    def get(self, request, *args, **kwargs):
        member_id = kwargs.get('member_id')
        member = Member.objects.get(member_id=member_id)

        project_name = request.GET.get('project_name')
        project_description = request.GET.get('project_description')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        teams = request.GET.get('teams')
        team_id = request.GET.get('team_id')
        team_name = request.GET.get('team_name')
        team_memo = request.GET.get('team_memo')
        team_members = request.GET.get('team_members')
        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        # APIエンドポイントを呼び出してメンバー情報を取得
        response = get_member_data(request, member_id)
        member_info = json.loads(response.content).get('member_data')

        context = {
            'member': member_info,
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date,
            'teams': teams,
            'team_id': team_id,
            'team_name': team_name,
            'team_memo': team_memo,
            'team_members': team_members,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        member_id = kwargs.get('member_id')
        member = Member.objects.get(member_id=member_id)
        member_name = request.POST.get('member_name')
        member_memo = request.POST.get('member_memo')

        member.name = member_name
        member.memo = member_memo
        member.save()

        return JsonResponse({'status': 'success'})

#チームメンバー編集保存
class TeamMemberEditSaveView(TemplateView):
    template_name = "team_edit.html"

    def post(self, request, *args, **kwargs):
        member_id = request.POST.get('member_id')
        member = Member.objects.get(member_id=member_id)
        member_name = request.POST.get('member_name')
        member_memo = request.POST.get('member_memo')

        member.name = member_name
        member.memo = member_memo
        member.save()

        return JsonResponse({'status': 'success'})

#プロジェクトリスト
class ProjectlistView(TemplateView):
    template_name="projectlist.html"
class progress_within_ProjectlistView(TemplateView):
    template_name="progress_within_projectlist.html"

# プロジェクトリスト表示
def projectListView(request):
    template_name = "progress_within_projectlist.html"
    ctx = {}
    query = request.GET.get('q')
    qs = Project.objects.all()
    qs=qs.filter(complete_flag=0,deletion_flag=0)
    if query:
        qs = qs.filter(project_name__icontains=query)  # プロジェクト名でフィルタリング

    ctx["project_list"] = qs
    return render(request, template_name, ctx)

# 過去プロジェクト
class post_ProjectlistView(TemplateView):
    template_name="post_projectlist.html"

# 過去プロジェクト表示
def Post_projectListView(request):
    template_name = "post_projectlist.html"
    ctx = {}
    query = request.GET.get('p')
    qs = Project.objects.all()
    qs=qs.filter(complete_flag=1,deletion_flag=0)
    if query:
        qs = qs.filter(project_name__icontains=query)  # プロジェクト名でフィルタリング

    ctx["project_list"] = qs
    return render(request, template_name, ctx)


# プロジェクト詳細表示
class Project_detailView(TemplateView):
    template_name="project_detail.html"


from django.shortcuts import render, get_object_or_404
from .models import Project, ProjectAffiliationTeam, ProjectProgressStatus

#プロジェクト詳細表示時に利用
#project_idを使用してデータを取得
def project_detail_view(request, project_id):
    # プロジェクトを取得
    #project_idに当てはまるprojectテーブルのデータを取得
    project = get_object_or_404(Project, project_id=project_id)

    #プロジェクトに関連するチームを取得
    #プロジェクト所属チームテーブルのprojectに当てはまるデータを取得
    teams = ProjectAffiliationTeam.objects.filter(project=project).select_related('team')

    # プロジェクトに関連するフェーズを取得
    # 上と同じ感じ
    phases = ProjectProgressStatus.objects.filter(project=project)

    context = {
        #プロジェクトテーブルの情報
        'project': project,
        #プロジェクト所属チームテーブルの情報
        'teams': teams,
        #フェーズテーブルの情報
        'phases': phases,
    }
    # 情報を保持した状態でrender
    return render(request, 'project_detail.html', context)



# プロジェクト詳細変更モーダル保存時
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Project
from django.views.decorators.http import require_http_methods
@require_http_methods(["GET", "POST"])
# プロジェクト詳細変更モーダル保存時
def project_detail_update(request, project_id):
    """
    プロジェクト詳細の更新処理を行うビュー関数

    Args:
        request (HttpRequest): HTTPリクエスト
        project_id (int): 更新対象のプロジェクトID

    Returns:
        HttpResponse: プロジェクト詳細ページまたはエラーメッセージを含むレンダリング結果
    """
    # テンプレート名の定義
    templatename = f"project_detail.html"

    # 指定されたIDのプロジェクトを取得（削除されていないプロジェクトのみ）
    project = get_object_or_404(Project, project_id=project_id, deletion_flag=False)

    if request.method == "POST":
        try:
            # POSTデータから各プロジェクト情報を取得
            project_name = request.POST.get('project_name')
            project_description = request.POST.get('project_description')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            # 必須項目の入力チェック
            if not all([project_name, project_description, start_date, end_date]):
                # 必須項目が未入力の場合、エラーメッセージを表示して再表示
                messages.error(request, '全ての必須項目を入力してください。')
                return render(request, templatename, {
                    'project': project,
                    'project_name': project_name,
                    'project_description': project_description,
                    'start_date': start_date,
                    'end_date': end_date,
                })

            # 開始日と終了日の論理チェック
            if start_date > end_date:
                # 開始日が終了日より後の場合、エラーメッセージを表示して再表示
                messages.error(request, '開始日は終了日よりも前の日付である必要があります。')
                return render(request, templatename, {
                    'project': project,
                    'project_name': project_name,
                    'project_description': project_description,
                    'start_date': start_date,
                    'end_date': end_date,
                })

            # プロジェクト情報の更新
            project.project_name = project_name
            project.project_detail = project_description
            project.project_start_date = start_date
            project.project_end_date = end_date

            # 更新日時の設定
            project.update_date = timezone.now()

            # プロジェクト情報の保存
            project.save()

            # 成功メッセージの追加
            messages.success(request, 'プロジェクトが正常に更新されました。')







            # プロジェクトを取得
            #project_idに当てはまるprojectテーブルのデータを取得
            project = get_object_or_404(Project, project_id=project_id)

            #プロジェクトに関連するチームを取得
            #プロジェクト所属チームテーブルのprojectに当てはまるデータを取得
            teams = ProjectAffiliationTeam.objects.filter(project=project).select_related('team')

            # プロジェクトに関連するフェーズを取得
            # 上と同じ感じ
            phases = ProjectProgressStatus.objects.filter(project=project)

            context = {
                #プロジェクトテーブルの情報
                'project': project,
                #プロジェクト所属チームテーブルの情報
                'teams': teams,
                #フェーズテーブルの情報
                'phases': phases,
            }
            # 情報を保持した状態でrender
            return render(request, 'project_detail.html', context)





        except Exception as e:
            # 予期しないエラーが発生した場合のエラーハンドリング
            messages.error(request, f'更新中にエラーが発生しました: {str(e)}')
            return render(request, templatename, {
                'project': project,
                'project_name': project_name,
                'project_description': project_description,
                'start_date': start_date,
                'end_date': end_date,
            })

    # GETリクエストの場合、プロジェクト詳細ページを表示
    return render(request, templatename, {'project': project})







# フェーズ追加時
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Project
from django.views.decorators.http import require_http_methods
@require_http_methods(["GET", "POST"])
# フェーズ追加
def project_detail_update(request, project_id):

    # テンプレート名の定義
    templatename = f"project_detail.html"

    # 指定されたIDのプロジェクトを取得（削除されていないプロジェクトのみ）
    project = get_object_or_404(Project, project_id=project_id, deletion_flag=False)

    if request.method == "POST":
        try:
            # POSTデータから各プロジェクト情報を取得
            project_name = request.POST.get('project_name')
            project_description = request.POST.get('project_description')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            phase_name = request.POST.get('phase_name')
            end_date2 = request.POST.get('end_date2')

            # 必須項目の入力チェック
            if not all([project_name, project_description, start_date, end_date,phase_name,end_date2]):
                # 必須項目が未入力の場合、エラーメッセージを表示して再表示
                messages.error(request, '全ての必須項目を入力してください。')
                return render(request, templatename, {
                    'project': project,
                    'project_name': project_name,
                    'project_description': project_description,
                    'start_date': start_date,
                    'end_date': end_date,
                })

            # 開始日と終了日の論理チェック
            if start_date > end_date:
                # 開始日が終了日より後の場合、エラーメッセージを表示して再表示
                messages.error(request, '開始日は終了日よりも前の日付である必要があります。')
                return render(request, templatename, {
                    'project': project,
                    'project_name': project_name,
                    'project_description': project_description,
                    'start_date': start_date,
                    'end_date': end_date,
                })

            # プロジェクト情報の更新
            project.project_name = project_name
            project.project_detail = project_description
            project.project_start_date = start_date
            project.project_end_date = end_date

            # 更新日時の設定
            project.update_date = timezone.now()

            # プロジェクト情報の保存
            project.save()

            # 成功メッセージの追加
            messages.success(request, 'プロジェクトが正常に更新されました。')
            # プロジェクトを取得
            #project_idに当てはまるprojectテーブルのデータを取得
            project = get_object_or_404(Project, project_id=project_id)

            #プロジェクトに関連するチームを取得
            #プロジェクト所属チームテーブルのprojectに当てはまるデータを取得
            teams = ProjectAffiliationTeam.objects.filter(project=project).select_related('team')

            # プロジェクトに関連するフェーズを取得
            # 上と同じ感じ
            phases = ProjectProgressStatus.objects.filter(project=project)

            context = {
                #プロジェクトテーブルの情報
                'project': project,
                #プロジェクト所属チームテーブルの情報
                'teams': teams,
                #フェーズテーブルの情報
                'phases': phases,
            }
            # 情報を保持した状態でrender
            return render(request, 'project_detail.html', context)





        except Exception as e:
            # 予期しないエラーが発生した場合のエラーハンドリング
            messages.error(request, f'更新中にエラーが発生しました: {str(e)}')
            return render(request, templatename, {
                'project': project,
                'project_name': project_name,
                'project_description': project_description,
                'start_date': start_date,
                'end_date': end_date,
            })

    # GETリクエストの場合、プロジェクト詳細ページを表示
    return render(request, templatename, {'project': project})








class team_detailView(TemplateView):
    template_name="team_detail.html"

def team_detail_view(request, team_id):
    template_name = "post_projectlist.html"
    ctx = {}
    team = get_object_or_404(Project, team_id=team_id)
    qs = Project.objects.all()
    qs=qs.filter(complete_flag=1,deletion_flag=0)
    if team:
        qs = qs.filter(project_id=team)

    ctx["team_detail"] = qs
    return render(request, template_name, ctx)

    # ctx["project_list"] = qsequest, self.template_name, {'members': members}

    # 過去プロジェクト
def Post_projectListView(request):
    template_name = "past_project_list.html"
    ctx = {}
    query = request.GET.get('p')
    qs = Project.objects.all()
    qs=qs.filter(complete_flag=1,deletion_flag=0)
    if query:
        qs = qs.filter(project_name__icontains=query)  # プロジェクト名でフィルタリング

    ctx["project_list"] = qs
    return render(request, template_name, ctx)

class Past_ProjectView(TemplateView):
    template_name = "past_project_view.html"

def project_detail(request, project_id):
    template_name = "past_project_view.html"
    project = get_object_or_404(Project, pk=project_id)
    return render(request, template_name, {'project': project})

class Past_ProjectDeletingView(TemplateView):
    template_name = "past_project_deleting_confirmation.html"

class Project_DeletedView(TemplateView):
    template_name = "project_deleted.html"

class Project_Save_CompleteView(TemplateView):
    template_name = "project_save_complete.html"
