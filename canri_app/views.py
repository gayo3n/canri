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

class NewProjectView(TemplateView):
    template_name = "create_new_project.html"




class MemberListMakeView(TemplateView):
    template_name = "memberList_make.html"
    
    memberID_list = []
    
    def get(self, request, *args, **kwargs):
        form = SearchForm(request.GET) 
        # 初期状態で全メンバーを取得
        members = Member.objects.all()

        context = {
            'form': form,
            'members': members
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # 初期状態で全メンバーを取得
        members = Member.objects.all()
        
        # 検索処理
        search_query = request.POST.get('query', '')
        if search_query:
            members = members.filter(name__icontains=search_query)
        
        # リクエストから 'member_id' を取得
        member_id = request.POST.get('member_id')
        memberID_list = request.POST.getlist('memberID_list')
        member_name = None  # 初期化しておく

        if member_id:
            #  member_id でメンバーを検索
                member = Member.objects.get(id=member_id)
                member_name = member.name
                print(f"Member Name: {member_name}")
                
        if member_id is not None:
            memberID_list.append(member_id)  # リストに 'member_id' を追加

        
        # データをテンプレートに渡す
        context = {
            'members': members,
            'memberID_list': memberID_list,
            'member_name' : member_name
        }
        return render(request, self.template_name, context)



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
    template_name = "memberlit_delete_complete.html"

class ManagementAccountView(TemplateView):
    template_name = "management_account.html"


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

        # 入力された情報を保持した状態でnew_project_edit.htmlに遷移
        return render(request, self.template_name, {'project': project_data})

class CreateTeamView(TemplateView):
    template_name = "create_team.html"
class ProjectlistView(TemplateView):
    template_name="projectlist.html"


def projectListView(request):
    template_name = "projectlist.html"
    ctx = {}
    query = request.GET.get('q')
    qs = Project.objects.all()
    qs=qs.filter(complete_flag=0,deletion_flag=0)
    if query:
        qs = qs.filter(project_name__icontains=query)  # プロジェクト名でフィルタリング

    ctx["project_list"] = qs
    return render(request, template_name, ctx)
