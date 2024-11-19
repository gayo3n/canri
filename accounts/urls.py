from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from . import views

from.views import acclogin, logincomp, logout, account_create, account_create_complete,manage_account, account_delete, account_change_employee,ManagementAccountView

app_name = 'accounts'

urlpatterns = [
    # アカウント管理
    path('login/', views.acclogin, name="login"), #ログイン
    path('login_complete/', views.logincomp, name='login_complete'), #ログイン完了
    path('login_failure/', views.LoginFailView.as_view(), name='login_failure'), #ログイン失敗
    path('logout_confirmation/', views.logout, name='logout_confirmation'), #ログアウト
    path('logout_complete/', views.LogoutCompView.as_view(), name='logout_complete'), #ログアウト完了
    # path('management_account/', views.ManagementAccountView, name='manage_account'), #アカウント一覧

    path('management_account/', ManagementAccountView.as_view(), name='manage_account'),
    path('management_account/account_creating/', views.account_create, name='account_creating'), #アカウント作成
    path('management_account/create/account_create_complete/', views.account_create_complete, name='account_create_complete'),  #アカウント作成完了
    path('account_delete/', views.account_delete, name='account_delete'), #アカウント削除
    path('account_change_employee/', views.account_change_employee, name='account_change_employee'),
    
    # アイコン
    # path('change_employee/', views.AccountChangeEmployeeView.as_view(), name='account_change_employee'),
    # path('change_employee/complete/', views.AccountChangeEmployeeCompleteView.as_view(), name='account_change_complete_employee'),

    #path('#/<int:pk>/', views.ManageAcc.as_view(), name='#'),   #アカウントページ用url
]
