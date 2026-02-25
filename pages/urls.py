from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('screen1/', views.screen1, name='screen1'),
    path('screen2/', views.screen2, name='screen2'),
    path('screen3/', views.screen3, name='screen3'),
    path('achievements/', views.student_achievements, name='student_achievements'),
    path('mobile/chat/', views.mobile_chat, name='mobile_chat'),
    path('get-mobile-app/', views.get_mobile_app, name='get_mobile_app'),
    path('faq/', views.faq, name='faq'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('offline/', views.offline, name='offline'),
    path('serviceworker.js', views.serviceworker, name='serviceworker'),
]
