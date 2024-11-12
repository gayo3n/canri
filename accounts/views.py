from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.views import View, generic
from django.contrib.auth.views import LoginView as AuthLoginView
from django.views.generic.base import TemplateView
from .forms import CustomUserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import AbstractUser
from django.views.generic.edit import CreateView


User = get_user_model()

class MwnuView(TemplateView):
    template_name = 'menu.html'

# class LoginView(TemplateView):
#     form_class = UserForm
#     template_name = 'login.html'
#     def post(self, request, *args, **kwargs):
#         return render(request, 'login_complete.html')

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


class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk']
    

class ManageAcc(OnlyYouMixin, generic.DetailView):
    model = User
    template_name = '#'

# class AccCreateForm(UserCreationForm):
#     template_name = 'account_creating.html'

    #class Meta:
    #     model = User
    #     fields = ('userid', 'password', 'username',)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for field in self.fields.values():
    #         field.widget.attrs['class'] = 'form-control'
    #         field.widget.attrs['required'] = ''


    #         print(field.label)
    #         if field.label == '姓':
    #             field.widget.attrs['autofocus'] = ''
    #             field.widget.attrs['placeholder'] = '大原'
    #         elif field.label == '名':
    #             field.widget.attrs['placeholder'] = '太郎'
    #         elif field.label == 'メールアドレス':
    #             field.widget.attrs['placeholder'] = '***＠gmail.com'


class AccCreateView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'account_creating.html'
    success_url = '/account_created/'  

class AccCreatedView(TemplateView):
    template_name = "account_created.html"