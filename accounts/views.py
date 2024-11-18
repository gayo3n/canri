from django.contrib.auth.views import LogoutView, LoginView 
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth import login, get_user_model, logout as auth_logout
from django.urls import reverse
from django.views import View, generic
from django.views.generic.base import TemplateView
from .forms import AccountAddForm, UserCreationForm, UserForm, LoginForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import AbstractUser
from django.views.generic.edit import CreateView
from django.http import HttpResponse
from .models import User
from django.contrib.auth.mixins import LoginRequiredMixin


USer = get_user_model()

# class LoginView(TemplateView):
#     form_class = UserForm
#     template_name = 'login.html'
#     def post(self, request, *args, **kwargs):
#         return render(request, 'login_complete.html')

def acclogin(request):
    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                return redirect('login_complete', user.user_id)
    else:
        form = LoginForm()
    
    context = {'form': form}
    return render(request, 'login.html', context)

def logincomp(request, user_id):
    return render(request, 'login_complete.html', {'user_id': user_id})

    
class LoginFailView(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'login_failure.html')
    
# class LogoutConfView(TemplateView):
#     def post(self, request):
#         return redirect('logout_confirmation')

class LogoutCompView(TemplateView):
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


class Account_User(LoginRequiredMixin, TemplateView):
    template_name = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class LoginFailView(LoginRequiredMixin, TemplateView):
    template_name = 'login_failure.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.exclude(username=self.request.user.username)
        return context
 

def manage_account(request):
    acc = {}
    user = User.objects.all()
    acc['object_list']
    return render(request, 'management_account.html')


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

def account_create(request):
    form = AccountAddForm(request.POST)
    if form.is_valid():
            form.save()
            return redirect('account_create_complete')
    else:
        form = UserForm()

    return render(request, "account_create.html")


def account_chaenge(request):
    user_change = get_object_or_404(User, user=user_id)
    form = UserForm(instance=user_change)
    return render(request, 'account_change.html', {'form': form})

def account_change_complete(request):
    user_change = get_object_or_404(User, user=user_id)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user_change)
        if form.is_valid():
            form.save()
    return render(request, 'account_change_complete')

def account_delete(request, user):
    template_name = "account_delete.html"
    obj = get_object_or_404(User, user=user)
    context = {'object': obj}
    return render(request, template_name, context)