# urls.py
from django.urls import path
from . import views
from .views import projectListView,Post_projectListView,project_detail_view,project_detail_update,project_phase_add,project_phase_edit,project_phase_delete,project_phase_coplete,ProjectComplete
from . import api
from django.conf import settings
from django.conf.urls.static import static

app_name = 'canri_app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    # メンバーリスト
    path('memberlist/',                                     views.MemberListView.as_view(),             name='memberlist'),
    path('memberlist/make/',                                views.MemberListMakeView.as_view(),         name='memberlist_make'),
    path('memberlist/make/complete/',                       views.MemberListMakeCompleteView.as_view(), name='memberlist_make_complete'),
    path('memberlist/edit/<int:category_id>/',              views.MemberListEditView.as_view(),         name='memberlist_edit'),
    path('memberlist/edit/complete/',                       views.MemberListEditCompleteView.as_view(), name='memberlist_edit_complete'),
    path('memberlist/delete/<int:category_id>/',            views.MemberListDeleteView.as_view(),       name='memberlist_delete'),
    path('memberlist/delete/complete/<int:category_id>/',   views.MemberListDeleteCompleteView.as_view(),name='memberlist_delete_complete'),
    # メンバー
    path('member/make/',                                views.MemberMakeView.as_view(),             name='member_make'),
    path('member/edit/<int:member_id>/',                views.MemberEditView.as_view(),             name='member_edit'),
    path('member/upload_csv/',                          views.FileUploadView.as_view(),             name='member_csv_upload'),
    path('member/overwrite/',                           views.MemberOverwriteView.as_view(),        name='member_overwrite'),
    path('member/make/complete/',                       views.MemberMakeCompleteView.as_view(),     name='member_make_complete'),
    path('member/edit/complete/<int:member_id>/',       views.MemberEditCompleteView.as_view(),     name='member_edit_complete'),
    path('member/delete/<int:member_id>/',              views.MemberDeleteView.as_view(),           name='member_delete'),
    path('member/delete/complete/<int:member_id>/',     views.MemberDeleteCompleteView.as_view(),   name='member_delete_complete'),


    #新規プロジェクト作成
    path('new_project/',                        views.NewProjectView.as_view(),         name='new_project'),
    path('new_project_edit/',                   views.NewProjectEditView.as_view(),     name='new_project_edit'),
    path('new_project_edit/back/',              views.NewProjectEdit2View.as_view(),    name='new_project_edit2'),
    path('create_team/',                        views.CreateTeamView.as_view(),         name='create_team'),
    path('create_team2/',                       views.CreateTeam2View.as_view(),        name='create_team2'),                            #チーム追加
    path('create_team2/back/',                  views.CreateTeam2BackView.as_view(),    name='create_team2_back'),
    path('create_team3/',                       views.CreateTeam3View.as_view(),        name='create_team3'),
    path('create_team3/save/',                  views.SaveTeamView.as_view(),           name='create_team3_save'),
    path('save_new_project/',                   views.SaveNewProjectView.as_view(),     name='save_new_project'),
    path('team_edit/<int:team_id>/',            views.TeamEditView.as_view(),           name='team_edit'),
    path('team_edit/complete/',                 views.TeamEditCompleteView.as_view(),   name='team_edit_complete'),
    path('team_member_edit/',                   views.TeamMemberEditView.as_view(),     name='team_member_edit'),
    path('team_member_edit/<int:member_id>/',   views.TeamMemberEditView.as_view(),     name='team_member_edit'),
    path('team_member_edit_save/',              views.TeamMemberEditSaveView.as_view(), name='team_member_edit_save'),
    path('team_delete/',                        views.TeamDeleteView.as_view(),         name='team_delete'),


    #進行中プロジェクト関連
    path('project/',                                projectListView,        name='project'),                #進行中プロジェクト一覧表示
    path('project/<int:project_id>/',               project_detail_view,    name='project_detail'),         #進行中プロジェクト 一覧でプロジェクト選択時利用 詳細表示
    path('project_detail_update/<int:project_id>/', project_detail_update,  name='project_detail_update'),  #プロジェクト詳細更新時利用
    path('project_complete/<int:project_id>/',      ProjectComplete,        name='project_complete'),       #プロジェクト完了時利用
    # フェーズ関係
    path('project_phase_add/<int:project_id>/',     project_phase_add,      name='project_phase_add'),      #フェーズ追加
    path('project_phase_edit/<int:project_id>/',    project_phase_edit,     name='project_phase_edit'),     #フェーズ編集
    path('project_phase_delete/<int:project_id>/',  project_phase_delete,   name='project_phase_delete'),   #フェーズ削除
    path('project_phase_coplete/<int:project_id>/', project_phase_coplete,  name='project_phase_coplete'),  #フェーズ完了
    # 新規チーム作成関連
    path('project_detail_create_team/',     views.project_detail_Create_TeamView.as_view(),     name='project_detail_create_team'), #チーム作成1遷移不明？？？
    path('project_detail_create_team2/',    views.project_detail_Create_Team2View.as_view(),    name='project_detail_create_team2'),#チーム作成2
    path('project_detail_create_team3/',    views.project_detail_CreateTeam3View.as_view(),     name='project_detail_create_team3'),#チーム作成3
    path('project_detail_save_team/',       views.project_detail_SaveTeamView.as_view(),        name='project_detail_save_team'),   #チーム作成保存
    # チーム編集関連
    path('project_team_edit/<int:team_id>/',    views.projectTeamEditView.as_view(), name='project_team_edit'),   #チーム編集表示とチーム編集保存時に利用(pastとget)
    path('project_team_delete/<int:team_id>/',  views.project_team_delete.as_view(), name="project_team_delete"), #チーム削除処理


    # 過去プロジェクト
    path('past_project/',                                           views.Past_ProjectListView.as_view(),       name='past_project'),
    path('past_project_view/<int:project_id>/',                     views.Past_ProjectView.as_view(),           name='past_project_view'),
    path('past_project_deleting_confirmation/<int:project_id>/',    views.Past_ProjectDeletingView.as_view(),   name='past_project_deleting_confirmation'),
    path('past_project_deleted/<int:project_id>/',                  views.Past_Project_DeletedView.as_view(),   name='past_project_deleted'),
    path('save_past_project/',                                      views.Project_Save_CompleteView.as_view(),  name='save_past_project'),
    path('feedback/save/',                                          views.FeedbackSaveView.as_view(),           name='feedback_save'),
    path('feedback/delete/',                                        views.delete_feedback,                      name='delete_feedback'),
    path('team_edit_past/<int:team_id>/',                           views.TeamEditPastView.as_view(),           name='team_edit_past'),
    path('team_edit_past/complete/<int:project_id>/',               views.TeamEditPastCompleteView.as_view(),   name='team_edit_past_complete'),
    path('team_member_edit_past/',                                  views.TeamMemberEditPastView.as_view(),     name='team_member_edit_past'),
    path('team_member_edit_past/<int:member_id>/',                  views.TeamMemberEditPastView.as_view(),     name='team_member_edit_past'),
    path('team_member_edit_save_past/',                             views.TeamMemberEditSavePastView.as_view(), name='team_member_edit_save_past'),
    path('delete_past_project/',                                    views.DeletePastProjectView.as_view(),      name='delete_past_project'),

    # APIエンドポイント
    path('api/get_member_data/<int:member_id>/',                api.get_member_data,            name='get_member_data'),
    path('api/get_members_by_member_list/<int:category_id>/',   api.get_members_by_member_list, name='get_members_by_member_list'),
    path('api/create_team/',                                    api.create_team_api,            name='create_team_api'),
    path('api/get_teams_by_project/<int:project_id>/',          api.get_teams_by_project,       name='get_teams_by_project'),
    path('api/get_team_members/<int:team_id>/',                 api.get_team_members,           name='get_team_members'),
    path('api/get_team_data/<int:team_id>/',                    api.get_team_data,              name='get_team_data'),
    path('api/save_team/',                                      api.save_team_api,              name='save_team'),
    path('api/save_project/',                                   api.save_project_api,           name='save_project_api'),
    path('api/delete_team/',                                    api.delete_team_api,            name='delete_team_api'),
    path('api/save_member_memo/',                               api.save_member_memo,           name='save_member_memo'),
    path('api/move_member_to_team/',                            api.move_member_to_team,        name='move_member_to_team'),
    path('api/get_p_project_detail/<int:project_id>/',          api.get_p_project_detail,       name='get_p_project_detail'),
    path('api/get_members_by_project/<int:project_id>/',        api.get_members_by_project,     name='get_members_by_project'),
    path('api/get_feedbacks_by_project/<int:project_id>/',      api.get_feedbacks_by_project,   name='get_feedbacks_by_project'),

    # エラー画面
    path('trigger-error/',  views.trigger_error,            name='trigger_error'),
    path('error500html/',   views.errorhtmlView.as_view(),  name='error_500'),
    
] 