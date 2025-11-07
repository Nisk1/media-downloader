from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('download-progress/', views.download_progress, name='download_progress'),
    path('archives/list/', views.list_archives, name='list_archives'),
    path('archives/create/', views.create_archive, name='create_archive'),
    path('archives/delete/', views.delete_archive, name='delete_archive'),
    path('stop-download/', views.stop_download_view, name='stop_download'),

]
