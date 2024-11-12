from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from . import views

from.views import account_login

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('login_complete/', views.LoginCompView.as_view(), name='login_complete'),
    path('login_failure/', views.LoginCompView.as_view(), name='login_failure'),

    path('logout_confirmation/', views.LogoutConfView.as_view(), name='logout_confirmation'),
    path('management_account/', views.ManagementAccountView.as_view(), name='management_account'),
    path('logout_complete/', views.LogoutCompView.as_view(), name='logout_complete'),
]
