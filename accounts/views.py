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
    
# class LogoutConfView(TemplateView):
#     def post(self, request):
#         return redirect('logout_confirmation')

class CustomLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('login_complete')  # ログイン成功時のリダイレクト先

class LoginCompView(TemplateView):
    template_name = 'login_complete.html'

class LogoutConfView(TemplateView):
    template_name = 'logout_confirmation.html'

class LogoutCompView(TemplateView):
    template_name = 'logout_complete.html'

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
                user_id=form.cleaned_data['user_id'],
                name=form.cleaned_data['name'],
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
    else:
        form = UserForm()
    return render(request, 'account_create_complete.html', {'form':form})

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
    

def account_delete(request, name):
    obj = get_object_or_404(User, name=name)
    if request.method == 'POST':
        obj.delete()
        return redirect('accounts:account_delete_complete')
    return render(request, 'account_delete.html', {'object':obj})

def account_delete_complete(request):
    return render(request, 'account_delete_complete.html')
