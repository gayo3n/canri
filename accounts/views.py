from django.contrib.auth.views import LogoutView, LoginView 
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth import login, get_user_model, logout, authenticate as auth_logout
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
class ManagementAccountView(TemplateView):
    template_name = "management_account.html"

    def get(self, request, *args, **kwargs):
        # データベースから全ユーザーを取得
        users = User.objects.all()

        # コンテキストにユーザー情報を渡す
        context = {
            'users': users,  # 全ユーザーをテンプレートに渡す
        }

        return render(request, 'management_account.html', context)

class AccountCreateView(TemplateView):
    template_name = "account_create.html"

class CreateCompleteView(TemplateView):
    template_name = "account_create_complete.html"

class AccountChangeView(TemplateView):
    template_name = "account_change.html"

class AccountChangeCompleteView(TemplateView):
    template_name = "account_change_complete.html"

class AccountDeleteView(TemplateView):
    template_name = "account_delete.html"

class DeleteCompleteView(TemplateView):
    template_name = "account_delete_complete.html"

# アイコン
class AccountChangeEmployeeView(TemplateView):
    template_name = "account_change_employee.html"

class AccountChangeEmployeeCompleteView(TemplateView):
    template_name = "account_change_complete_employee.html"


# class LoginFailView(LoginRequiredMixin, TemplateView):
#     template_name = 'login_failure.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['users'] = User.objects.exclude(username=self.request.user.username)
#         return context

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
