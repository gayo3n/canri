from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    # アカウント管理
    path('login/', views.login_view, name="login"), #ログイン
    path('login_complete/', views.login_complete_view, name='login_complete'), #ログイン完了
    path('login_failure/', views.LoginFailView.as_view(), name='login_failure'), #ログイン失敗
    path('logout_confirmation/', views.logout, name='logout_confirmation'), #ログアウト
    path('logout_complete/', views.LogoutCompView.as_view(), name='logout_complete'), #ログアウト完了

    path('management_account/', views.ManagementAccountView.as_view(), name='management_account'), #アカウント一覧
    path('management_account/create/', views.AccountCreateView.as_view(), name='account_create'), #アカウント作成
    path('management_account/create/account_create_complete/', views.CreateCompleteView.as_view(), name='account_create_complete'),  #アカウント作成完了
    path('account_delete/', views.AccountDeleteView.as_view(), name='account_delete'), #アカウント削除
    path('account_change/', views.AccountChangeView.as_view(), name='account_change'),
    path('account_delete/complete/', views.DeleteCompleteView.as_view(), name='account_delete_complete'),
    path('account_change_employee/complete/', views.AccountChangeCompleteView.as_view(), name='account_change_complete'),

    # アイコン
    path('change_employee/', views.AccountChangeEmployeeView.as_view(), name='account_change_employee'),
    path('change_employee/complete/', views.AccountChangeEmployeeCompleteView.as_view(), name='account_change_complete_employee'),

    #path('#/<int:pk>/', views.ManageAcc.as_view(), name='#'),   #アカウントページ用url
]
