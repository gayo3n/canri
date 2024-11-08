# urls.py
from django.urls import path
from . import views

app_name = 'canri_app'

urlpatterns = [
    path('menberlist/', views.MemberListView.as_view(), name='menberlist'),
    path('', views.IndexView.as_view(), name='index'),
    path('memberList_make/', views.MemberListMakeView.as_view(), name='memberList_make'),
    path('member_make/', views.MemberMakeView.as_view(), name='member_make'),
]
