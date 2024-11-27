from django.contrib import admin
from django.urls import path, include
from . import views

from.views import logincomp, logout, create, account_create_complete, account_delete, account_delete_complete

app_name = 'accounts'

urlpatterns = [
    # アカウント管理
    path('login/', views.login_view, name="login"), #ログイン
    path('login_complete/<int:user_id>/', views.logincomp, name='login_complete'), #ログイン完了
    path('login_failure/', views.LoginFailView.as_view(), name='login_failure'), #ログイン失敗
    path('logout_confirmation/', views.logout, name='logout_confirmation'), #ログアウト
    path('logout_complete/', views.LogoutCompView.as_view(), name='logout_complete'), #ログアウト完了
    path('management_account/', views.Manage_Account.as_view(), name='manage_account'), #アカウント一覧
    path('management_account/account_creating/', views.create, name='account_create'), #アカウント作成
    path('management_account/create/account_create_complete/', views.account_create_complete, name='account_create_complete'),  #アカウント作成完了
    path('account_delete/<str:name>/', views.account_delete, name='account_delete'), #アカウント削除
    path('account_delete_complete/', views.account_delete_complete, name="account_delete_complete"),
    path('account_change_employee', views.account_change, name='account_change_employee'),
    path('account_change_complete/<int:pk>/', views.account_change_complete, name='account_change_complete'),
    
    # アイコン
    path('change_employee/', views.AccountChangeEmployeeView.as_view(), name='account_change_employee'),
    path('change_employee/complete/', views.AccountChangeEmployeeCompleteView.as_view(), name='account_change_complete_employee'),

    #path('#/<int:pk>/', views.ManageAcc.as_view(), name='#'),   #アカウントページ用url
]
