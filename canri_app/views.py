from django.shortcuts import render
from django.views.generic.base import TemplateView

# Create your views here.
class IndexView (TemplateView):
    template_name = "index.html"


class MemberListMakeView(TemplateView):
    template_name = "memberList_make.html"


class MemberMakeView(TemplateView):
    template_name = "member_make.html"