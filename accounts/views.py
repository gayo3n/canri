from django.contrib.auth.views import LogoutView, LoginView 
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth import login, get_user_model, logout, authenticate as auth_logout
from django.urls import reverse_lazy
from django.views import View, generic
from django.views.generic.base import TemplateView
from .forms import AccountAddForm, UserCreationForm, UserForm, LoginForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import AbstractUser
from django.views.generic.edit import CreateView
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from .models import User

class LoginFailView(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'login_failure.html')
    
class LogoutConfView(TemplateView):
    def post(self, request):
        return redirect('logout_confirmation')

class CustomLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('login_complete')  # ログイン成功時のリダイレクト先

class LoginCompView(TemplateView):
    template_name = 'login_complete.html'

class LogoutCompView(TemplateView):
    template_name = 'logout_complete.html'

class LogoutConfView(TemplateView):
    template_name = 'logout_confirmation.html'

<<<<<<< HEAD
class LogoutCompView(TemplateView):
    template_name = 'logout_complete.html'

=======
class AccLoginView(LoginView):
    def post(self, request, *arg, **kwargs):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            user = User.objects.get(name=name)
            login(request, user)
            return redirect('accounts:login_complete')
        return render(request, 'login.html', {'form': form})
        
    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    
    # def post(self, request):
    #     if request.method == "POST":
    #         form = LoginForm(request, data=request.POST)
    #         if form.is_valid():
    #             user = form.get_user()
    #             if user:
    #                 login(request, user)
    #                 return redirect('accounts:login_complete')
    #     else:
    #         form = LoginForm()
        
    #     param = {
    #         'form': form,
    #     }
    #     return render(request, 'login.html', param)
    
    # def get(self, request):
    #     form = LoginForm()
    #     param = {
    #         'form': form,
    #     }
    #     return render(request, 'login.html', param)
>>>>>>> 3547ad0db95613f81de3bfeb27c9bf03e428e8ae


def logout(request):
    auth_logout(request)
    request.session.flush()
    print('ログアウト処理が実行されました')
    if request.user.is_authenticated:
        print('ユーザーはまだ認証されています')
        return redirect('accounts:logout_confirmation')
    else:
        print('ログアウト完了')
        return redirect('accounts:logout_complete')

# アカウント管理
class Manage_Account(TemplateView):
    template_name = "management_account.html"

    def get(self, request, *args, **kwargs):
        # データベースから全ユーザーを取得
        users = User.objects.all()

        # コンテキストにユーザー情報を渡す
        context = {
            'users': users,  # 全ユーザーをテンプレートに渡す
        }

        return render(request, 'management_account.html', context)


# アイコン

def account_change_employee(request, pk):
    item = User.objects.get(user_id=pk)
    form = UserForm(instance=item)
    if request.method == "POST":
        form = UserForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("accounts:account_change_complete_employee", pk=pk)
    context = {
         "form": form,
        "item": item
        }
    return render(request, 'account_change_employee.html', context)

def account_change_complete_employee(request, pk):
    return render(request, 'account_change_complete_employee.html', {'pk':pk})



def create(request):
    if request.method == 'GET':
        # リクエストメソッドがGETの場合、空のフォームをインスタンス化
        form = AccountAddForm()
    elif request.method == 'POST':
        # リクエストメソッドがPOSTの場合、POSTデータでフォームをインスタンス化
        form =AccountAddForm(request.POST)
        if form.is_valid():
            user_id=form.cleaned_data['user_id']
            if User.objects.filter(user_id=user_id).exists():
                form.add_error('user_id', 'このアカウントIDは既に使用されています。')
            else:
                # フォームが有効な場合、クリーンデータを使用して新しいユーザーを作成
                user = User.objects.create_user(
                    user_id=form.cleaned_data['user_id'],
                    name=form.cleaned_data['name'],
                    password=form.cleaned_data['password']
                )
                # アカウント作成完了を示すテンプレートをレンダリング
                return redirect('accounts:account_create_complete')
    # アカウント作成フォームのテンプレートをレンダリング
    context = {'form': form}
    return render(request, 'account_create.html', context)


def account_create_complete(request):
    form = UserForm(request.POST)
    if form.is_valid():
        # フォームが有効な場合、データを保存
        form.save()
        # アカウント作成完了のテンプレートをレンダリング
        return render(request, 'account_create_complete.html')
    else:
        # フォームが無効な場合、新しいフォームをインスタンス化
        form = UserForm()
    # アカウント作成完了のテンプレートをフォームと共にレンダリング
    return render(request, 'account_create_complete.html', {'form': form})

def manage_account_change(request, pk):
    item = User.objects.get(user_id=pk)
    form = UserForm(instance=item)
    if request.method == "POST":
        form = UserForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("accounts:account_change_complete", pk=pk)
        
    context = {
        "form": form,
        "item": item
    }
    return render(request, 'account_change.html', context)

def account_change_complete(request, pk):
    return render(request, 'account_change_complete.html', {'pk':pk})
    
# アカウント削除
def account_delete(request, name):
    obj = get_object_or_404(User, name=name)
    if request.method == 'POST':
        obj.delete()
        return redirect('accounts:account_delete_complete')
    return render(request, 'account_delete.html', {'object':obj, 'name': name})

def account_delete_complete(request):
    return render(request, 'account_delete_complete.html')
