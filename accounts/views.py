from django.contrib.auth.views import LogoutView, LoginView as AuthLoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, get_user_model
from django.urls import reverse
from django.views import View, generic
from django.views.generic.base import TemplateView
from .forms import AccountAddForm, UserCreationForm, UserForm, AccountAddForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import AbstractUser
from django.views.generic.edit import CreateView
from django.http import HttpResponse
from .models import User


USer = get_user_model()

class LoginView(TemplateView):
    form_class = UserForm
    template_name = 'login.html'
    def post(self, request, *args, **kwargs):
        return render(request, 'login_complete.html')

class LoginCompView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'login_complete.html')
    
class LoginFailView(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'login_failure.html')
    
class LogoutConfView(TemplateView):
    template_name = 'logout_confirmation.html'

class LogoutCompView(TemplateView):
    def post(self, request, *args, **kwargs):
        return render(request, 'logout_complete.html')

# def create(request):
#     if request.method == 'GET':
#         form = AccountAddForm
#         context = {
#             'form':form
#         }
#         return render(request, 'account_create.html', context)
#     elif request.method == 'POST':
#         form = AccountAddForm(request.POST)
#         if form.is_valid():
#             get_user_model().objects.create_user(
#                 user_id=form.cleaned_data['user_id'],
#                 password=form.cleaned_data['password'],
#                 name=form.cleaned_data['name']
#             )
#             return redirect('management_account/account_creating/account_create_complete/')
#         context = {
#             'form': form
#         }
#         return render(request, 'account_create.html', context)

def manage_account(request):
    template_name = 'management_account.html'
    acc = {}
    user = User.objects.all()
    acc['object_list']


def account_create_complete(request):
    form = UserForm(request.POST)
    if form.is_valid():
        form.save()
    return render(request, 'account_create_complete.html')

class AccountLogin(AuthLoginView):
    template_name = "login.html"
    def post(self, request, *args, **kwargs):
        form = UserForm(data=request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            try:
                user = User.objects.get(name=name)
                if user.check_password(password):
                    login(request, user)
                    return redirect('login_complete')  # URL名を使用
                else:
                    error_message = "ユーザー名またはパスワードが正しくありません。"
            except User.DoesNotExist:
                error_message = "ユーザー名またはパスワードが正しくありません。"
        else:
            error_message = "フォームにエラーがあります。"

        return render(request, 'login.html', {'form': form, 'error_message': error_message})

account_login = AccountLogin.as_view()

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