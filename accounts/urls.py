from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from . import views

from.views import account_login

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('login/login_complete/', views.LoginCompView.as_view(), name='login_complite'),
    
    path('logout_confirmation/', views.LogoutConfView.as_view(), name='logout_confirmation'),
    path('logout_complete/', views.LogoutCompView.as_view(), name='logout_complete'),


]
