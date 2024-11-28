from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    # アカウント管理
    path('login/', views.LoginView.as_view(template_name='login.html'), name='login'),
    path('login_complete/', views.LoginCompView.as_view(), name='login_complete'), #ログイン完了
    path('logout_complete/', views.LogoutCompView.as_view(), name='logout_complete'), #ログアウト完了
    path('login_failure/', views.LoginFailView.as_view(), name='login_failure'), #ログイン失敗
    path('logout_confirmation/', views.LogoutConfView.as_view(), name='logout_confirmation'), #ログアウト

    path('management_account/', views.Manage_Account.as_view(), name='manage_account'), #アカウント一覧
    path('management_account/account_creating/', views.create, name='account_create'), #アカウント作成
    path('management_account/create/complete/', views.account_create_complete, name='account_create_complete'),  #アカウント作成完了
    path('account_delete/<str:name>/', views.account_delete, name='account_delete'), #アカウント削除
    path('account_delete_complete/', views.account_delete_complete, name="account_delete_complete"),
    path('manage_account_change/<int:pk>/', views.manage_account_change, name='manage_account_change'),
    path('account_change_complete/<int:pk>/', views.account_change_complete, name='account_change_complete'),
    
    # アイコン
    path('change_employee/<int:pk>/', views.account_change_employee, name='account_change_employee'),
    path('change_employee_complete/', views.account_change_complete_employee, name='account_change_complete_employee'),

    #path('#/<int:pk>/', views.ManageAcc.as_view(), name='#'),   #アカウントページ用url
]
