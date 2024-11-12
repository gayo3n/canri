# urls.py
from django.urls import path
from . import views, api

app_name = 'canri_app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('memberlist/', views.MemberListView.as_view(), name='memberlist'),
    path('memberlist/make/', views.MemberListMakeView.as_view(), name='memberList_make'),
    path('member_make/', views.MemberMakeView.as_view(), name='member_make'),
    path('memberlist/memberlist_delete/', views.MemberListDeleteView.as_view(), name='memberlist_delete'),
    path('memberlist/memberlist_delete/complete/', views.MemberListDeleteOkView.as_view(), name='memberlist_delete'),

    path('member_search/', views.MemberSearchView.as_view(), name='member_search'),
    
    path('management_account/', views.ManagementAccountView.as_view(), name='management_account'),
    
    # API関係
    path('get_member_data/<int:member_id>/', api.get_member_data, name='get_member_data'),#メンバー情報取得
    path('get_members/<int:member_list_id>/', api.get_members_by_member_list, name='get_members_by_member_list'),#メンバーリスト取得
    path('create_team/', api.create_team_api, name='create_team'),#チーム作成
]
