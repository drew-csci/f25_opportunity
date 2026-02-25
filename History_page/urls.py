from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('experiences/', views.experiences_achievements_view, name='experiences_achievements'),
]
