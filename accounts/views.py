from pyexpat.errors import messages
from django.contrib.auth.views import LogoutView, LoginView, PasswordChangeView, PasswordChangeDoneView
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth import login, get_user_model, logout as auth_logout, authenticate, update_session_auth_hash
from django.utils import timezone
from django.urls import reverse_lazy
from django.db import transaction
from django.views import View, generic
from django.views.generic.base import TemplateView
from .forms import AccountAddForm, UserCreationForm, UserForm, LoginForm, PasswordChangeForm, MySetPasswordForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import AbstractUser
from django.views.generic.edit import CreateView
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from .models import User


# ログイン失敗画面
class LoginFailView(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'login_failure.html')
    
# ログアウト確認画面
class LogoutConfView(TemplateView):
    def post(self, request):
        return redirect('logout_confirmation')

# ログイン画面
class CustomLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('login_complete')  # ログイン成功時のリダイレクト先

# ログイン完了画面
class LoginCompView(TemplateView):
    template_name = 'login_complete.html'

# ログアウト完了画面
class LogoutCompView(TemplateView):
    template_name = 'logout_complete.html'

# ログアウト
class LogoutConfView(TemplateView):
    template_name = 'logout_confirmation.html'


# ログイン機能
class AccLoginView(LoginView):
    def post(self, request, *arg, **kwargs):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            password = form.cleaned_data.get('password')
            
            # authenticate を呼び出して認証を試みる
            user = authenticate(request, username=name, password=password)
            
            if user is not None:
                if user.deletion_flag:  # 削除フラグが立っている場合はログイン拒否
                    form.add_error(None, 'このアカウントは削除されています。')
                    return render(request, 'login.html', {'form': form})
                
                login(request, user)
                return redirect('accounts:login_complete')
        
        # ログインできなかった場合のエラーメッセージ
        form.add_error(None, 'ログインに失敗しました。')
        return render(request, 'login.html', {'form': form})

# ログアウト機能
def logout(request):
    auth_logout(request)
    request.session.flush()
    print('ログアウト処理が実行されました')
    if request.user.is_authenticated:
        print('ユーザーはまだ認証されています')
        return redirect('accounts:logout_confirmation')
    else:
        print('ログアウト完了')
        return redirect('accounts:logout_complete')

# アカウント管理
class Manage_Account(TemplateView):
    template_name = "management_account.html"

    def get(self, request, *args, **kwargs):
        # 削除フラグがFalseかつスーパーユーザーでないユーザーのみを取得
        users = User.objects.filter(deletion_flag=False, is_superuser=False)
        
        context = {
            'users': users,  # 全ユーザーをテンプレートに渡す
        }
        return render(request, 'management_account.html', context)


# アイコン

def account_change_employee(request, pk):
    # ユーザー情報を取得
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = MySetPasswordForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            # ユーザー名の変更を処理
            user.name = request.POST.get('name')
            user.save()
            # 再ログイン処理
            password = form.cleaned_data.get('new_password1')
            user = authenticate(request, username=user.name, password=password)
            if user is not None:
                login(request, user)
                return redirect("accounts:account_change_complete_employee", pk=pk)
            else:
                return redirect("accounts:login")
    else:
        form = MySetPasswordForm(user=user)

    context = {
        "user": user,
        "form": form
    }
    return render(request, 'account_change_employee.html', context)

def account_change_complete_employee(request, pk):
    return render(request, 'account_change_complete_employee.html', {'pk': pk})

# アカウント作成
def create(request):
    if request.method == 'GET':
        # リクエストメソッドがGETの場合、空のフォームをインスタンス化
        form = AccountAddForm()
    elif request.method == 'POST':
        # リクエストメソッドがPOSTの場合、POSTデータでフォームをインスタンス化
        form =UserForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            name = form.cleaned_data['name']
            # 入力された情報がDB上に存在するか検証
            user_id_exists = User.objects.filter(user_id=user_id).exists()
            name_exists = User.objects.filter(name=name).exists()

            # ユーザーIDが存在している時のエラーメッセージを表示
            if user_id_exists:
                form.add_error('user_id', 'このアカウントIDは既に使用されています。')
            
            # ユーザー名が存在している時のエラーメッセージを表示
            if name_exists:
                form.add_error('name', 'この名前のユーザーはすでに存在しています。')
            
                # フォームが有効な場合、クリーンデータを使用して新しいユーザーを作成
            if not user_id_exists and not name_exists:    
                user = User.objects.create_user(
                    user_id=form.cleaned_data['user_id'],
                    name=form.cleaned_data['name'],
                    password=form.cleaned_data['password'],
                    administrator_flag=False  # ここでadministrator_flagを設定
                )
                # アカウント作成完了を示すテンプレートをレンダリング
                return redirect('accounts:account_create_complete')
    # アカウント作成フォームのテンプレートをレンダリング
    context = {'form': form}
    return render(request, 'account_create.html', context)

# アカウント作成完了画面
def account_create_complete(request):
    form = UserForm(request.POST)
    if form.is_valid():
        # フォームが有効な場合、データを保存
        form.save()
        # アカウント作成完了のテンプレートをレンダリング
        return render(request, 'account_create_complete.html')
    else:
        # フォームが無効な場合、新しいフォームをインスタンス化
        form = UserForm()
    # アカウント作成完了のテンプレートをフォームと共にレンダリング
    return render(request, 'account_create_complete.html', {'form': form})


# アカウント一覧からのパスワード変更
def account_change(request, pk):
    # アカウント編集のテンプレートを表示
    template_name = 'account_change.html'
    # ユーザー情報を取得
    user = get_object_or_404(User, pk=pk)
    form = MySetPasswordForm(user=user)
    context = {
        'form':form,
        'user':user
    }
    return render(request, template_name, context)


def account_change(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        user.name = request.POST.get('name')
        password = request.POST.get('password')
        user.set_password(password)
        user.save()

        item = User.objects.get(pk=pk)

    context = {
        "user": item
    }
    return render(request, 'account_change_employee.html', context)

    
def account_change_complete(request, pk):
    # ユーザー情報を取得
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = MySetPasswordForm(user=user, data=request.POST)
        if form.is_valid():
            # ユーザー情報を保存
            form.save()
            return redirect('accounts:account_change_complete', pk=pk)
        else:
            for field, errors in form.errors.items(): 
                for error in errors: print(f'Error in {field}: {error}') # 送信されたデータのデバッグ 
            print(f'POST data: {request.POST}')
            # 入力されたパスワードが確認���と違う場合エラーメ��セージと変更画面を表示
            return render(request, 'account_change.html', {'form':form, 'user':user})
    else:
        form = MySetPasswordForm(user=user)
    # パスワード変更完了画面を表示
    return render(request, 'account_change_complete.html', {'form':form,'user':user})


# アカウント削除
def account_delete(request, name):
    # 該当ユーザーを取得（削除フラグが立っていないユーザーのみを対象）
    obj = get_object_or_404(User, name=name, deletion_flag=False)
    
    if request.method == 'POST':
        # 論理削除：削除フラグを立てる
        obj.deletion_flag = True
        obj.deletion_date = timezone.now()  # 削除日時を記録
        obj.save()
        return redirect('accounts:account_delete_complete')
    
    return render(request, 'account_delete.html', {'object': obj, 'name': name})

def account_restore(request, name):
    # 削除フラグが立っているユーザーを取得
    obj = get_object_or_404(User, name=name, deletion_flag=True)
    
    if request.method == 'POST':
        obj.restore()  # 論理削除を解除
        return redirect('accounts:manage_account')
    
    return render(request, 'account_restore.html', {'object': obj, 'name': name})


def account_delete_complete(request):
    return render(request, 'account_delete_complete.html')