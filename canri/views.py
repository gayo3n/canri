from django.shortcuts import render
from django.views.generic.base import TemplateView

class LoginView(TemplateView):
    template_name = 'login.html'

class LoginCompView(TemplateView):
    template_name = 'login_complite.html'

class LogoutView(TemplateView):
    template_name = 'logout.html'

class MwnuView(TemplateView):
    template_name = 'menu.html'