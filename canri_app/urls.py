# urls.py
from django.urls import path
from . import views, api
from .views import projectListView,Post_projectListView
app_name = 'canri_app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('memberlist/', views.MemberListView.as_view(), name='memberlist'),
    path('memberlist/make/', views.MemberListMakeView.as_view(), name='memberList_make'),
    path('memberlist/add/', views.MemberListAddView.as_view(), name='memberList_add'),
    path('memberlist/make/complete', views.MemberListMakeCompleteView.as_view(), name='memberList_make_complete'),
    path('member_make/', views.MemberMakeView.as_view(), name='member_make'),
    path("memberlist/make/complete/", views.MemberListMakeCompleteView.as_view(), name="memberList_make_complete"),
    path('member_make/complete/', views.MemberMakeCompleteView.as_view(), name='member_make_complete'),
    path('member_make/delete/', views.MemberMakeDeleteView.as_view(), name='member_make_delete'),
    path('member_make/delete/complete/', views.MemberListDeleteOkView.as_view(), name='memberlist_delete_complete'),
    path('memberlist/memberlist_delete/', views.MemberListDeleteView.as_view(), name='memberlist_delete'),
    path('memberlist/memberlist_delete/complete/', views.MemberListDeleteOkView.as_view(), name='memberlist_delete_complete'),
<<<<<<< HEAD

    
=======
    path('member_search/', views.MemberSearchView.as_view(), name='member_search'),
>>>>>>> ac71f44c2585ab6747be79a834bafdae6e71361d
    path('management_account/', views.ManagementAccountView.as_view(), name='management_account'),

    path('new_project/', views.NewProjectView.as_view(), name='new_project'),    
    path('new_project_edit/', views.NewProjectEditView.as_view(), name='new_project_edit'),    
    path('create_new_project/', views.NewProjectView.as_view(), name='create_new_project'),    


    path('progress_within_projectlist/', views.progress_within_ProjectlistView.as_view(), name='projectlist'),
    path('post_projectlist/', views.progress_within_ProjectlistView.as_view(), name='post_projectlist'),
    path('project/', projectListView, name='project'),
    path('post_project/', Post_projectListView, name='post_project'),


    # API関係
    path('get_member_data/<int:member_id>/', api.get_member_data, name='get_member_data'),#メンバー情報取得
    path('get_members/<int:member_list_id>/', api.get_members_by_member_list, name='get_members_by_member_list'),#メンバーリスト取得
    path('create_team/', api.create_team_api, name='create_team'),#チーム作成
    path('get_teams_by_project/<int:project_id>', api.get_teams_by_project, name='get_teams_by_project'),#プロジェクトチーム取得
    path('get_team_members/<int:team_id>', api.get_team_members, name='get_team_members'),#チームメンバー取得
]
