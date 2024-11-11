# urls.py
from django.urls import path
from . import views

app_name = 'canri_app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('memberlist/', views.MemberListView.as_view(), name='memberlist'),
    path('memberlist/memberList_make/', views.MemberListMakeView.as_view(), name='memberList_make'),
    path('member_make/', views.MemberMakeView.as_view(), name='member_make'),
    path('management_account/', views.ManagementAccountView.as_view(), name='management_account'),
]
