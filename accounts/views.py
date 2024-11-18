from django.contrib.auth.views import LogoutView
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.urls import reverse
from django.views import View, generic
from django.contrib.auth.views import LoginView as AuthLoginView
from django.views.generic.base import TemplateView
from .forms import AccountAddForm, UserForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import AbstractUser
from django.views.generic.edit import CreateView


User = get_user_model()

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
    template_name = 'logout_confirmation_complete.html'
    def post(self, request, *args, **kwargs):
        return render(request, 'logout_complete.html')


# アカウント管理
class ManagementAccountView(TemplateView):
    template_name = "management_account.html"

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


class Create(generic.CreateView):
    template_name = 'account_creating.html'
    form_class = UserForm

    def form_valid(self, form):
        user = form.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('account_created')  # URL名を正しく指定
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["process_name"] = "Login"
        return context
    
class CreateComp(generic.TemplateView):
    template_name = 'account_created.html'


class ManagementAccountView(TemplateView):
    template_name = "management_account.html"

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
