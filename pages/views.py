from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import FeedPost # Import the new model

def welcome(request):
    return render(request, 'pages/welcome.html')

@login_required
def peer_activities(request):
    feed_posts = FeedPost.objects.all().select_related('user') # Fetch all posts and related user
    context = {
        'feed_posts': feed_posts
    }
    return render(request, 'pages/peer_activities.html', context)

@login_required
def screen1(request):
    role = request.user.user_type.title() if hasattr(request.user, 'user_type') else 'User'
    return render(request, 'pages/screen1.html', {'role': role})

@login_required
def screen2(request):
    role = request.user.user_type.title() if hasattr(request.user, 'user_type') else 'User'
    return render(request, 'pages/screen2.html', {'role': role})

@login_required
def screen3(request):
    role = request.user.user_type.title() if hasattr(request.user, 'user_type') else 'User'
    return render(request, 'pages/screen3.html', {'role': role})
