from django.urls import path
from . import views
from . import buggy_view   # <-- add this import

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('screen1/', views.screen1, name='screen1'),
    path('screen2/', views.screen2, name='screen2'),
    path('screen3/', views.screen3, name='screen3'),
    path('peer-activities/', views.peer_activities, name='peer_activities'), # New route for peer activities
    path('buggy/', buggy_view.buggy_search, name='buggy_search'),  # <-- add this route
]
