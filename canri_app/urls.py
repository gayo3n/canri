from django.urls import path
from . import views

app_name ='canri_app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('menberlist/', views.IndexView.as_view(), name='menberlist'),
    path('management_account/', views.IndexView.as_view(), name='management_account'),
    # path('ongoingproject/', views.OngoinprojectView.as_view(), name='ongoingproject') # 進行中プロジェクト
]