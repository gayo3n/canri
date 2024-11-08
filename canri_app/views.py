# views.py
from django.views.generic.base import TemplateView

class IndexView(TemplateView):
    template_name = "index.html"

class MemberListView(TemplateView):
    template_name = "menberlist.html"

class ManagementAccountView(TemplateView):
    template_name = "management_account.html"
