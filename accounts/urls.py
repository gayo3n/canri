from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from . import views

from.views import account_login, account_create, account_create_complete,manage_account, account_delete

urlpatterns = [
    #path('login/', views.LoginView.as_view(), name='login'),
    path('login_complete/', views.LoginCompView.as_view(), name='login_complete'), #ログイン完了
    path('login_failure/', views.LoginFailView.as_view(), name='login_failure'), #ログイン失敗
    path('logout_confirmation/', views.LogoutConfView.as_view(), name='logout_confirmation'), #ログアウト
    path('management_account/', views.manage_account, name='manage_account'),
    path('logout_complete/', views.LogoutCompView.as_view(), name='logout_complete'), #ログアウト完了
    path('management_account/account_creating/', views.account_create, name='account_creating'), #アカウント作成
    path('management_account/create/account_create_complete/', views.account_create_complete, name='account_create_complete'),  
    path('login/', account_login, name="login"), #ログイン
    path('account_delete/', views.account_delete, name='account_delete'), 
]
