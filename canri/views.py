from django.shortcuts import render
from django.views import View
from django.views.generic.base import TemplateView

class LoginView(TemplateView):
    template_name = 'login.html'

class LogoutView(TemplateView):
    template_name = 'logout.html'

class MwnuView(TemplateView):
    template_name = 'menu.html'

class LoginCompView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'login_complite.html')