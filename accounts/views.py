from django.shortcuts import render, redirect
from django.contrib.auth.models import Account
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView
from . forms import LoginForm, UserCreateForm
from django.contrib.auth.forms import AuthenticationForm

class Account_login(View):
    def post(self, request, *arg, **kwargs):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = Account.objects.get(username=username, password=password)
            login(request, user)
            return redirect('/')
        return render(request, 'accounts/login.html', {'form': form,})
    
    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        return render(request)



class Create_account(CreateView):
    def post(self, request, *args, **kwargs):
        form = UserCreateForm(data=request.POST)
        if form.is_valid():
            form.save()
            # フォームから'usename'を読み取る
            username = form.cleaned_data.get('username')
            # フォームから'password'
            password = form.changed_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
        return render(request, 'create.html', {'form': form,})
    
    def get(self, request, *args, **kwargs):
        form = UserCreateForm(request.POST)
        return render(request, 'create.html', {'form': form,})
    
create_account = Create_account.as_view()


def index(request):
    return render(request, 'index.html')