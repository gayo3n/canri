from django.urls import path
from . import views

app_name ='canri_app'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'), # トップページ
    #path('/ongoingproject', views.OngoinprojectView.as_view(), name='ongoingproject') # 進行中プロジェクト
]