from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from . import views

from.views import account_login

app_name = 'accounts'

urlpatterns = [
    #path('login/', views.LoginView.as_view(), name='login'),
    path('login_complete/', views.LoginCompView.as_view(), name='login_complete'), #ログイン完了
    path('login_failure/', views.LoginFailView.as_view(), name='login_failure'), #ログイン失敗
    path('logout_confirmation/', views.LogoutConfView.as_view(), name='logout_confirmation'), #ログアウト
    path('management_account/', views.ManagementAccountView.as_view(), name='management_account'),
    path('logout_complete/', views.LogoutCompView.as_view(), name='logout_complete'), #ログアウト完了
    path('management_account/account_creating/', views.Create.as_view(), name='account_creating'),
    path('account_created/', views.CreateComp.as_view(), name='account_created'),
    path('login/', account_login, name="login"),
    # アカウント管理
    path('management_account/', views.ManagementAccountView.as_view(), name='management_account'),
    path('management_account/create/', views.AccountCreateView.as_view(), name='account_create'),
    path('management_account/create/complete/', views.CreateCompleteView.as_view(), name='account_create_complete'),
    path('management_account/delete/', views.AccountDeleteView.as_view(), name='account_delete'),
    path('management_account/delete/complete/', views.DeleteCompleteView.as_view(), name='account_delete_complete'),
    path('management_account/change/', views.AccountChangeView.as_view(), name='account_change'),
    path('management_account/change/complete/', views.AccountChangeCompleteView.as_view(), name='account_change_complete'),

    # アイコン
    path('change_employee/', views.AccountChangeEmployeeView.as_view(), name='account_change_employee'),
    path('change_employee/complete/', views.AccountChangeEmployeeCompleteView.as_view(), name='account_change_complete_employee'),

    #path('#/<int:pk>/', views.ManageAcc.as_view(), name='#'),   #アカウントページ用url
]
