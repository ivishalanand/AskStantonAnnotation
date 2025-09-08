from django.urls import path
from . import views

app_name = 'session_viewer'

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:session_id>/', views.session_detail, name='session_detail'),
]