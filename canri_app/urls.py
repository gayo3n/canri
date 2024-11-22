# urls.py
from django.urls import path
from . import views
from .views import projectListView,Post_projectListView,project_detail_view,team_detail_view,project_detail_update
from .views import projectListView,Post_projectListView,project_detail_view,team_detail_view,project_detail
from . import api

app_name = 'canri_app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # メンバーリスト
    path('memberlist/', views.MemberListView.as_view(), name='memberlist'),
    path('memberlist/make/', views.MemberListMakeView.as_view(), name='memberList_make'),
    path('memberlist/make/complete/', views.MemberListMakeCompleteView.as_view(), name='memberList_make_complete'),
    
    path('memberlist/memberlist_delete/', views.MemberListDeleteView.as_view(), name='memberlist_delete'),
    path('memberlist/memberlist_delete/complete/', views.MemberListDeleteOkView.as_view(), name='memberlist_delete_complete'),
    # メンバー
    path('member_make/', views.MemberMakeView.as_view(), name='member_make'),
    path('member_make/complete/', views.MemberMakeCompleteView.as_view(), name='member_make_complete'),
    path('member_make/delete/', views.MemberMakeDeleteView.as_view(), name='member_make_delete'),
    path('member_make/delete/complete/', views.MemberMakeDeleteOkView.as_view(), name='member_make_delete_complete'),
    path('memberlist/memberlist_delete/', views.MemberListDeleteView.as_view(), name='memberlist_delete'),
    path('memberlist/memberlist_delete/complete/', views.MemberListDeleteOkView.as_view(), name='memberlist_delete_complete'),
    

    # path('member_search/', views.MemberSearchView.as_view(), name='member_search'),
    
    #新規プロジェクト作成
    path('new_project/', views.NewProjectView.as_view(), name='new_project'),    
    path('new_project_edit/', views.NewProjectEditView.as_view(), name='new_project_edit'),
    path('new_project_edit/back/', views.NewProjectEdit2View.as_view(), name='new_project_edit2'),
    path('create_team/', views.CreateTeamView.as_view(), name='create_team'),
    path('create_team2/', views.CreateTeam2View.as_view(), name='create_team2'),                            #チーム追加
    path('create_team2/back/', views.CreateTeam2BackView.as_view(), name='create_team2_back'),
    path('create_team3/', views.CreateTeam3View.as_view(), name='create_team3'),
    path('create_team3/save/', views.SaveTeamView.as_view(), name='create_team3_save'),
    path('save_new_project/', views.SaveNewProjectView.as_view(), name='save_new_project'),
    path('team_edit/<int:team_id>/', views.TeamEditView.as_view(), name='team_edit'),
    path('team_edit/complete/', views.TeamEditCompleteView.as_view(), name='team_edit_complete'),
    path('team_member_edit/', views.TeamMemberEditView.as_view(), name='team_member_edit'),
    path('team_member_edit/<int:member_id>/', views.TeamMemberEditView.as_view(), name='team_member_edit'),
    path('team_member_edit_save/', views.TeamMemberEditSaveView.as_view(), name='team_member_edit_save'),
    path('team_delete/', views.TeamDeleteView.as_view(), name='team_delete'),

    #プロジェクト一覧
    path('progress_within_projectlist/', views.progress_within_ProjectlistView.as_view(), name='projectlist'),
    path('post_projectlist/', views.progress_within_ProjectlistView.as_view(), name='post_projectlist'),
    path('project/', projectListView, name='project'),                                                      #進行中プロジェクト選択時利用

    #プロジェクト詳細
    # path('project_detail/', views.Project_detailView.as_view(), name='project_detail'),
    path('project/<int:project_id>/', project_detail_view, name='project_detail'),                          #進行中プロジェクト一覧でプロジェクト選択時利用
    path('project_detail_update/<int:project_id>/', project_detail_update, name='project_detail_update'),   #プロジェクト詳細更新時利用
    path('project_detail_create_team/', views.project_detail_Create_TeamView.as_view(), name='detail_create_team'),
    # path('project_detail_update/<int:project_id>/project/', project_detail_view, name='project_detail_a'),

    # 過去プロジェクト
    path('past_project/', Post_projectListView, name='past_project'),#過去プロジェクト選択時利用
    path('past_project_view/', views.Past_ProjectView.as_view(), name='past_project_view'),
    path('past_project/view/<int:id>/', views.project_detail, name='past_project_view'),
    path('past_project_deleting/', views.Past_ProjectDeletingView.as_view(), name='past_project_deleting_confirmation'),
    path('past_project_deleting/deleted/', views.Project_DeletedView.as_view(), name='project_deleted'),
    path('project_save/', views.Project_Save_CompleteView.as_view(), name='project_save_complete'),

    #チーム詳細
    # path('team_detail/',views.team_detailView.as_view(), name='team_detail'),
    # path('team/<int:team_id>/', team_detail_view, name='project_detail'),

    # APIエンドポイント
    path('api/get_member_data/<int:member_id>/', api.get_member_data, name='get_member_data'),
    path('api/get_members_by_member_list/<int:category_id>/', api.get_members_by_member_list, name='get_members_by_member_list'),
    path('api/create_team/', api.create_team_api, name='create_team_api'),
    path('api/get_teams_by_project/<int:project_id>/', api.get_teams_by_project, name='get_teams_by_project'),
    path('api/get_team_members/<int:team_id>/', api.get_team_members, name='get_team_members'),
    path('api/get_team_data/<int:team_id>/', api.get_team_data, name='get_team_data'),
    path('api/save_team/', api.save_team_api, name='save_team'),
    path('api/save_project/', api.save_project_api, name='save_project_api'),
    path('api/delete_team/', api.delete_team_api, name='delete_team_api'),
    path('api/save_member_memo/', api.save_member_memo, name='save_member_memo'),
    path('api/move_member_to_team/', api.move_member_to_team, name='move_member_to_team'),
]
