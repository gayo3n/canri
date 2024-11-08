# accounts/urls.py
from django.contrib import admin
from django.urls import path,include
<<<<<<< HEAD
from django.contrib.auth.views import LoginView, LogoutView

from accounts import views
=======
from django.contrib.auth.views import LoginView
from . import views
>>>>>>> 70846145f8d354ce44127a9aaf8a4748310d2a17



urlpatterns = [
    #path('admin/', admin.site.urls),
    #path('',include('app.urls')),
    path('', views.LoginView.as_view(), name='login'),
<<<<<<< HEAD
    path('login_complete/', views.LoginCompView.as_view(), name='login_complete'),
    path('logout/', views.LogoutView.as_view(), name='logout_confirmation'),
=======
    path('login_complite/', views.LoginCompView.as_view(), name='login_complite'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    path('management_account/', views.ManagementAccountView.as_view(), name='management_account'),
>>>>>>> 70846145f8d354ce44127a9aaf8a4748310d2a17
]