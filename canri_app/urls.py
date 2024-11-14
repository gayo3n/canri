# urls.py
from django.urls import path
from . import views
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

    
    path('member_search/', views.MemberSearchView.as_view(), name='member_search'),
    path('management_account/', views.ManagementAccountView.as_view(), name='management_account'),
    
    #新規プロジェクト作成
    path('new_project/', views.NewProjectView.as_view(), name='new_project'),    
    path('new_project_edit/', views.NewProjectEditView.as_view(), name='new_project_edit'),
    path('create_team/', views.CreateTeamView.as_view(), name='create_team'),
    path('create_team2/', views.CreateTeam2View.as_view(), name='create_team2'),
    path('create_team3/', views.CreateTeam3View.as_view(), name='create_team3'),
    path('save_new_project/', views.SaveNewProjectView.as_view(), name='save_new_project'),


    path('progress_within_projectlist/', views.progress_within_ProjectlistView.as_view(), name='projectlist'),
    path('post_projectlist/', views.progress_within_ProjectlistView.as_view(), name='post_projectlist'),
    path('project/', projectListView, name='project'),
    path('post_project/', Post_projectListView, name='post_project'),
]
