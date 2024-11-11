from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from . import views

from.views import account_login

urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('login_complete/', views.LoginCompView.as_view(), name='login_complete'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('management_account/', views.ManagementAccountView.as_view(), name='management_account'),

    path('login/', account_login, name="login1"),
]
