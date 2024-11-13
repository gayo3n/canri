# views.py
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import MemberList, Member, Feedback, MemberParameter, MemberCareer, JobTitleInformation, MemberHoldingQualification, Project
from django.utils import timezone
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
    

class MemberListMakeCompleteView(TemplateView):
    template_name = "memberList_make_complete.html"

class MemberSearchView(TemplateView):
    template_name = 'memberList_make.html'

    def get(self, request, *args, **kwargs):
        form = SearchForm(request.GET)  # GETパラメータをフォームに渡す
        members = Member.objects.all()  # 初期状態で全メンバーを取得

        # 検索処理
        search_query = request.GET.get('query', '')  # 'query' というキーで取得
        print(f"Search query: {search_query}")  # 入力内容を確認

        if (search_query):
            members = members.filter(name__icontains=search_query)
            print(f"Filtered members: {members}")  # フィルタリング結果を表示

        return render(request, self.template_name, {'members': members})

class MemberMakeView(TemplateView):
    template_name = "member_make.html"

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