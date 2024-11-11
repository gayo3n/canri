from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.views import View
from django.contrib.auth.views import LoginView as AuthLoginView
from django.views.generic.base import TemplateView
from .forms import LoginForm

User = get_user_model()

class LoginView(TemplateView):
    form_class = LoginForm
    template_name = 'login.html'

class LogoutView(TemplateView):
    template_name = 'logout.html'

class MwnuView(TemplateView):
    template_name = 'menu.html'

class LoginCompView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'login_complete.html')

class ManagementAccountView(TemplateView):
    template_name = "management_account.html"

class AccountLogin(AuthLoginView):
    def post(self, request, *args, **kwargs):
        form = LoginForm(data=request.POST)
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