from django.contrib.auth.views import LogoutView, LoginView 
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth import login, get_user_model, logout as auth_logout, authenticate
from django.urls import reverse
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

def login_view(request):
    # リクエストメソッドがPOSTかどうかを確認
    if request.method == "POST":
        # リクエストからユーザー名とパスワードを取得
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            # ユーザー名でユーザーを取得しようとする
            user = User.objects.get(username=username)
            # 提供されたパスワードが保存されたパスワードと一致するか確認
            if auth_logout(request, username=user.username, password=password):  # ハッシュ化されたパスワードを比較
                login(request, user)  # ユーザーをログインさせる
                return redirect("accounts:login_complete")  # ログイン完了ページにリダイレクト
            else:
                # パスワードが間違っている場合、エラーメッセージを表示
                return render(request, "login.html", {"error_message": "パスワードが正しくありません"})
        except User.DoesNotExist:
            # ユーザーが存在しない場合、エラーメッセージを表示
            return render(request, "login.html", {"error_message": "ユーザーが存在しません"})

    # リクエストメソッドがPOSTでない場合、ログインページを表示
    return render(request, "login.html")


@login_required  # ログイン必須にするデコレータ
def login_complete_view(request):
    return render(request, "login_complete.html")  # login_complete.htmlを表示

# class LoginView(TemplateView):
#     form_class = UserForm
#     template_name = 'login.html'
#     def post(self, request, *args, **kwargs):
#         return render(request, 'login_complete.html')

def acclogin(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user_id = form.cleaned_data.get('user_id')
            password = form.cleaned_data.get('password')
            user = authenticate(request, user_id=user_id, password=password)
            if user is not None:
                login(request, user)
                return redirect('login_complete', user_id=user.id)  
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logincomp(request, user_id):
    return render(request, 'login_complete.html', {'user_id': user_id})

    
class LoginFailView(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'login_failure.html')
    
# class LogoutConfView(TemplateView):
#     def post(self, request):
#         return redirect('logout_confirmation')

class LogoutCompView(TemplateView):
    template_name = 'logout_confirmation_complete.html'
    def post(self, request, *args, **kwargs):
        return render(request, 'logout_complete.html')

# class AccLoginView(LoginView):
#     def login(request):
#         if request.method == "POST":
#             form = LoginForm(request, data=request.POST)
#             if form.is_valid():
#                 user = form.get_user()
#                 if user:
#                     login(request, user)
#         else:
#             form = LoginForm()
        
#         param = {
#             'form': form,
#         }
#         return render(request, 'login.html', param)


def logout(request):
    auth_logout(request)
    return render(request, 'logout_confirmation.html')

# アカウント管理
def manage_account(request):
    template_name = "management_account.html"

    def get(self, request, *args, **kwargs):
        # データベースから全ユーザーを取得
        users = User.objects.all()

        # コンテキストにユーザー情報を渡す
        context = {
            'users': users,  # 全ユーザーをテンプレートに渡す
        }

        return render(request, 'management_account.html', context)


class AccountChangeView(TemplateView):
    template_name = "account_change.html"

class AccountChangeCompleteView(TemplateView):
    template_name = "account_change_complete.html"

# アイコン
class AccountChangeEmployeeView(TemplateView):
    template_name = "account_change_employee.html"

class AccountChangeEmployeeCompleteView(TemplateView):
    template_name = "account_change_complete_employee.html"


def create(request):
    if request.method == 'GET':
        form = AccountAddForm()
    elif request.method == 'POST':
        form = AccountAddForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                name=form.cleaned_data['name'],
                user_id=form.cleaned_data['user_id'],
                password=form.cleaned_data['password']
            )
            return render(request, 'account_create_complete.html', {'user_id': user.user_id})
    context = {'form': form}
    return render(request, 'account_create.html', context)


def account_create_complete(request):
    form = UserForm(request.POST)
    if form.is_valid():
        form.save()
    return render(request, 'account_create_complete.html')

# class AccountLogin(AuthLoginView):
#     template_name = "login.html"
#     def post(self, request, *args, **kwargs):
#         form = UserForm(data=request.POST)
#         if form.is_valid():
#             name = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             try:
#                 user = User.objects.get(name=name)
#                 if user.check_password(password):
#                     login(request, user)
#                     return redirect('login_complete')  # URL名を使用
#                 else:
#                     error_message = "ユーザー名またはパスワードが正しくありません。"
#             except User.DoesNotExist:
#                 error_message = "ユーザー名またはパスワードが正しくありません。"
#         else:
#             error_message = "フォームにエラーがあります。"

#         return render(request, 'login.html', {'form': form, 'error_message': error_message})

# account_login = AccountLogin.as_view()

def account_chaenge(request, name):
    user_change = get_object_or_404(User, name=name)
    form = UserForm(instance=user_change)
    return render(request, 'account_change_employee.html', {'form': form})

def account_change_complete(request, name):
    user_change = get_object_or_404(User, name=name)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user_change)
        if form.is_valid():
            form.save()
    return render(request, 'account_change_employee_complete.html')

def account_delete(request, name):
    obj = get_object_or_404(User, name=name)
    if request.method == 'POST':
        obj.delete()
        return redirect('account_delete_complete', name=name)
    return render(request, 'account_delete.html', {'object':obj})

def account_delete_complete(request, name):
    return render(request, 'account_delete_complete.html', name=name)
