from django.contrib import admin
from django.urls import path,include
from django.contrib.auth.views import LoginView
from canri import views



urlpatterns = [
    #path('admin/', admin.site.urls),
    #path('',include('app.urls')),
    path('', views.LoginView.as_view(), name='login'),
    path('login_complite/', views.LoginCompView.as_view(), name='login_complite'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]