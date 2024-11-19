# views.py
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import *
from .models import MemberList, Member, Feedback, MemberParameter, MemberCareer, JobTitleInformation, MemberHoldingQualification, Project,CareerInformation,MBTI,Credentials,Category
from django.utils import timezone
import json
from .forms import SearchForm
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.views import View
from .api import get_member_data


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

    def get(self, request, *args, **kwargs):
        member_list = MemberList.objects.all()  # MemberListの全データを取得
        categories = [member.category for member in member_list]  # 各MemberListから関連するCategoryを取得

        context = {
            "categories": categories  # 関連するCategoryのリストを渡す
        }
        return render(request, self.template_name, context)


class NewProjectView(TemplateView):
    template_name = "create_new_project.html"



# -----メンバーリスト作成-----
class MemberListMakeView(TemplateView):
    template_name = "memberList_make.html"

    def get(self, request, *args, **kwargs):
        form = SearchForm(request.GET)
        members = self.get_queryset()

        # セッションから memberID_list を取得
        memberID_list = request.session.get('memberID_list', [])

        context = {
            'form': form,
            'members': members,
            'memberID_list': memberID_list  # 現在のリストを表示
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # セッションから memberID_list を取得
        memberID_list = request.session.get('memberID_list', [])

        # メンバー追加処理
        member_id = request.POST.get('member_id')
        if member_id and member_id.isdigit():
            member_id = int(member_id)
            if member_id not in memberID_list:
                # メンバーが存在するか確認
                try:
                    Member.objects.get(member_id=member_id)  # メンバーIDの確認
                    memberID_list.append(member_id)  # リストに追加
                except Member.DoesNotExist:
                    print(f"Member with ID {member_id} not found")

        # セッションに memberID_list を保存
        request.session['memberID_list'] = memberID_list

        members = self.get_queryset()
        context = {
            'members': members, # 検索エリアメンバー
            'memberID_list': memberID_list  # 更新されたリストメンバー
        }
        return render(request, self.template_name, context)
    

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            members = Member.objects.filter(name__icontains=query)
        else:
            members = Member.objects.all()
        return members


# -----メンバーリスト保存-----
class MemberListMakeCompleteView(TemplateView):
    template_name = "memberlist_make_complete.html"

    def post(self, request, *args, **kwargs):
        # リスト名と詳細を取得
        member_list_name = request.POST.get('member_list_name')
        member_list_details = request.POST.get('member_list_details')

        if member_list_name and member_list_details:
            # 新しいカテゴリを作成
            category = Category(
                category_name=member_list_name,
                detail=member_list_details,
                creation_date=timezone.now()
            )
            category.save()

            # POSTデータから memberID_list を取得
            member_id_list = request.POST.getlist('memberID_list')

            # 各 member_id に対して MemberList を作成
            for member_id in member_id_list:
                try:
                    # メンバーを取得
                    member = Member.objects.get(member_id=member_id)
                    # MemberList オブジェクトを作成して保存
                    member_list = MemberList(
                        member=member,
                        category=category,
                        creation_date=timezone.now()
                    )
                    member_list.save()
                except Member.DoesNotExist:
                    print(f"Member with ID {member_id} not found")

            # 成功したらメンバーリストページにリダイレクト
            return redirect('canri_app:memberlist')
        else:
            # 入力漏れがあればエラーメッセージを表示
            context = {'error_message': 'すべてのフィールドを入力してください。'}
            return render(request, 'canri_app/memberlist_make.html', context)    # メンバー情報を表示するビュー
        

        
class MemberListMakeCancel(TemplateView):
    template_name = "memberlist.html"

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
    template_name = "memberlit_delete_complete.html"

class ManagementAccountView(TemplateView):
    template_name = "management_account.html"


#新規プロジェクト作成
class NewProjectView(TemplateView):
    template_name = "new_project.html"

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

        # 入力された情報を保持した状態でnew_project_edit.htmlに遷移
        return render(request, self.template_name, {'project': project_data, 'teams': teams})

class CreateTeamView(TemplateView):
    template_name = "create_team.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')

        # 入力された情報を保持した状態でcreate_team.htmlに遷移
        return render(request, self.template_name, {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date,
            'teams': teams
        })

class CreateTeam2View(TemplateView):
    template_name = "create_team2.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.getlist('teams')
        team_size = request.POST.get('team_size')
        team_type = request.POST.get('team_type')
        auto_generate = request.POST.get('auto_generate')
        categories = Category.objects.filter(deletion_flag=False)
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
                'auto_generate': auto_generate,
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

class CreateTeam3View(TemplateView):
    template_name = "create_team3.html"

class SaveNewProjectView(TemplateView):
    template_name = "save_new_project.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')

        # プロジェクトを保存するロジックをここに追加

        # 入力された情報を保持した状態でsave_new_project.htmlに遷移
        return render(request, self.template_name, {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date,
            'teams': teams
        })

#プロジェクトリスト
class ProjectlistView(TemplateView):
    template_name="projectlist.html"
class progress_within_ProjectlistView(TemplateView):
    template_name="progress_within_projectlist.html"


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



class post_ProjectlistView(TemplateView):
    template_name="post_projectlist.html"


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





class Project_detailView(TemplateView):
    template_name="project_detail.html"


from django.shortcuts import render, get_object_or_404
from .models import Project, ProjectAffiliationTeam, ProjectProgressStatus

def project_detail_view(request, project_id):
    # プロジェクトを取得
    project = get_object_or_404(Project, project_id=project_id)

    # プロジェクトに関連するチームを取得
    teams = ProjectAffiliationTeam.objects.filter(project=project).select_related('team')

    # プロジェクトに関連するフェーズを取得
    phases = ProjectProgressStatus.objects.filter(project=project)

    context = {
        'project': project,
        'teams': teams,
        'phases': phases,
    }

    return render(request, 'project_detail.html', context)



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


