from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('exam/', views.exam, name='exam'),
    path('result/<int:result_id>/', views.result, name='result'),
    path('review/<int:result_id>/', views.review, name='review'),
    path('download/<int:result_id>/', views.download_result, name='download_result'),
]