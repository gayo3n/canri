from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView
from .forms import LoginForm
from django.views import View
from django.contrib.auth.views import LoginView as AuthLoginView
from django.views.generic.base import TemplateView

class LoginView(TemplateView):
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
            username = form.cleaned_data.get('username')
            user = User.objects.get(username=username)
            login(request, user)
            return redirect('/login_complete')
        return render(request, 'login.html', {'form': form})

account_login = AccountLogin.as_view()
