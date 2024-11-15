# views.py
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import *
from .models import MemberList, Member, Feedback, MemberParameter, MemberCareer, JobTitleInformation, MemberHoldingQualification, Project,CareerInformation,MBTI,Credentials
from django.utils import timezone
import json
from .forms import SearchForm
from django.http import HttpResponseBadRequest, HttpResponseNotFound



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

        if (search_query):
            members = members.filter(name__icontains=search_query)

        return render(request, self.template_name, {'members': members})

    


class MemberListAddView(TemplateView):
    template_name = "memberList_make.html"
    memberList = MemberList.objects.all()

    def post(self, request, *args, **kwargs):
        # リクエストから 'member_id' を取得
        member_id = request.POST.get('member_id')
        memberID_list = []

        # member_id が数値であることを確認
        if member_id is not None:
            try:
                memberID_list = member_id
                return memberID_list
            except ValueError:
                # 数値に変換できなかった場合のエラーハンドリング
                return HttpResponseBadRequest("member IDを取得できませんでした。")
            
        return render(request, self.template_name, {"memberID_list": memberID_list})

        # # 取得したIDを使用して MemberList オブジェクトを取得
        # try:
        #     member_list = MemberList.objects.get(member_list_id=member_id)
        # except MemberList.DoesNotExist:
        #     return HttpResponseNotFound("Memberが見つかりません。")


class MemberListMakeCompleteView(TemplateView):
    template_name = "memberList_make_complete.html"


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
        member_lists = MemberList.objects.all()
            
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
                'member_lists': member_lists
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
                'member_lists': member_lists
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

    ctx["project_list"] = qsequest, self.template_name, {'members': members}
