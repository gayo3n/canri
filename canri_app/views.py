# views.py
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import *
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


