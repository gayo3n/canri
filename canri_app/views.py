# views.py
from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from .models import MemberList

class IndexView(TemplateView):
    template_name = "index.html"

class MemberListView(TemplateView):
    template_name = "memberlist.html"



class MemberListMakeView(TemplateView):
    template_name = "memberList_make.html"

    def search_view(request):
        query = request.GET.get('q')
        results = MemberList.objects.all()

        if query:
            results = results.filter(field_name__icontains=query)  # field_nameは検索対象のフィールドに置き換えてください

        return render(request, 'memberList_make.html', {'results': results})


class MemberMakeView(TemplateView):
    template_name = "member_make.html"
