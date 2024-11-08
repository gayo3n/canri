# urls.py
from django.urls import path
from .views import IndexView, MemberListView, ManagementAccountView

app_name = 'canri_app'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('menberlist/', MemberListView.as_view(), name='menberlist'),
    path('management_account/', ManagementAccountView.as_view(), name='management_account'),
]
