# views.py
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import MemberList, Member, Feedback, MemberParameter, MemberCareer, JobTitleInformation, MemberHoldingQualification
import json
from .forms import SearchForm
from django.http import HttpResponseBadRequest, HttpResponseNotFound



class IndexView(TemplateView):
    template_name = "index.html"

    def my_view(request):
        if request.user.is_authenticated:
            # ユーザーはログインしています
            
            template_name = "index.html"
            return render(request, template_name)
        else:
            # ユーザーはログインしていません
            return redirect('accounts:login/')


class MemberListView(TemplateView):
    template_name = "memberlist.html"

class NewProjectView(TemplateView):
    template_name = "create_new_project.html"

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
        members = Member.objects.all()  # 初期状態で全メンバーを取得

        # 検索処理
        search_query = request.GET.get('query', '')  # 'query' というキーで取得

        if search_query:
            members = members.filter(name__icontains=search_query)

        return render(request, self.template_name, {'members': members})


class MemberListAddView(TemplateView):
    template_name = "memberList_make.html"
    memberList = MemberList.objects.all()

    def post(self, request, *args, **kwargs):
        # リクエストから 'member_id' を取得
        member_id = request.POST.get('member_id')

        # member_id が数値であることを確認
        if member_id is not None:
            try:
                member_id = int(member_id)  # 数値に変換
            except ValueError:
                # 数値に変換できなかった場合のエラーハンドリング
                return HttpResponseBadRequest("Invalid member ID.")

        # 取得したIDを使用して MemberList オブジェクトを取得
        try:
            member_list = MemberList.objects.get(member_list_id=member_id)
        except MemberList.DoesNotExist:
            return HttpResponseNotFound("Member not found.")


class MemberListMakeCompleteView(TemplateView):
    template_name = "memberList_make_complete.html"


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


