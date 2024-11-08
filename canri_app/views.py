# views.py
from django.views.generic.base import TemplateView

class IndexView(TemplateView):
    template_name = "index.html"

class MemberListView(TemplateView):
    template_name = "menberlist.html"



class MemberListMakeView(TemplateView):
    template_name = "memberList_make.html"


class MemberMakeView(TemplateView):
    template_name = "member_make.html"
