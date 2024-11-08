from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView
from canri.views import LoginView, LogoutView
from . forms import LoginForm
from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import render
from django.views.generic.base import TemplateView



class LoginView(TemplateView):
    template_name = 'login.html'

class LogoutView(TemplateView):
    template_name = 'logout.html'

class MwnuView(TemplateView):
    template_name = 'menu.html'

class LoginCompView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'login_complite.html')

#ログイン機能
class Account_login(LoginView):
    def post(self, request, *arg, **kwargs):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            user = User.objects.get(username=username)
            login(request, user)
            return redirect('/login_complite')
        return render(request, 'login.html', {'form': form,})

    def get(self, request, *args, **kwargs):
         form = LoginForm(request.POST)
         return render(request, 'login.html', {'form': form,})

account_login = Account_login.as_view()


# アカウント作成
# class Create_account(CreateView):
#     def post(self, request, *args, **kwargs):
#         form = UserCreateForm(data=request.POST)
#         if form.is_valid():
#             form.save()
#             # フォームから'usename'を読み取る
#             username = form.cleaned_data.get('username')
#             # フォームから'password'を読み取る
#             password = form.changed_data.get('password')
#             user = authenticate(username=username, password=password)
#             login(request, user)
#             return redirect('/')
#         return render(request, 'create.html', {'form': form,})
    
#     def get(self, request, *args, **kwargs):
#         form = UserCreateForm(request.POST)
#         return render(request, 'create.html', {'form': form,})
    
#create_account = Create_account.as_view()