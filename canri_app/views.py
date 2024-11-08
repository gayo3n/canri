from django.shortcuts import render
from django.views.generic.base import TemplateView

# Create your views here.

class IndexView(TemplateView):

    def index_view(request):

        return render(request, 'index.html')


    template_name = 'index.html'