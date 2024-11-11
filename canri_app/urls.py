# urls.py
from django.urls import path
from . import views

app_name = 'canri_app'

urlpatterns = [
    path('menberlist/', views.MemberListView.as_view(), name='menberlist'),
    path('', views.IndexView.as_view(), name='index'),
    path('memberList_make/', views.MemberListMakeView.as_view(), name='memberList_make'),
    path('member_make/', views.MemberMakeView.as_view(), name='member_make'),
    path('api/get_member/<int:member_id>/', views.get_member_data, name='get_member_data'),
    path('api/get_members/<int:member_list_id>/', views.get_members_by_member_list, name='get_members_by_member_list'),
    path('api/create_team/', views.create_team_api, name='create_team'),
]
