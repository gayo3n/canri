# urls.py
from django.urls import path
from . import views

app_name = 'canri_app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('memberlist/', views.MemberListView.as_view(), name='memberlist'),
    path('memberlist/make/', views.MemberListMakeView.as_view(), name='memberList_make'),
    path('member_make/', views.MemberMakeView.as_view(), name='member_make'),
    path('member_search/', views.MemberSearchView.as_view(), name='member_search'),
    
    path('management_account/', views.ManagementAccountView.as_view(), name='management_account'),
    
    path('get_member_data/<int:member_id>/', views.get_member_data, name='get_member_data'),
    path('get_members/<int:member_list_id>/', views.get_members_by_member_list, name='get_members_by_member_list'),
    path('create_team/', views.create_team_api, name='create_team'),
]
